import re
import pymongo
import time
import random
import requests
import json
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    HEADERS_HTML, EXTRACTION_DATE
)
from items import ProductDataItem

# Configure Logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.headers = HEADERS_HTML
        
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        
        # Create indexes
        self.product_collection.create_index("unique_id", unique=True)
        logger.info("Connected to MongoDB")

    def fetch_pdp_html(self, url):
        """
        Fetches the PDP HTML with retries.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:                
                resp = requests.get(url, headers=self.headers, timeout=20)
                if resp.status_code == 200:
                    return resp.text
                elif resp.status_code == 404:
                    logger.error(f"  Product not found (404): {url}")
                    return None
            except Exception as e:
                logger.warning(f"  Retryable error for {url}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 + random.uniform(0, 1))
        return None

    def get_tab_content(self, sel, label):
        """
        Robustly finds a tab pane based on the navigation link text.
        """
        xpath = f"//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[contains(normalize-space(), '{label}')]/@href, '#')]"
        return sel.xpath(xpath)

    def parse_nutritional_table(self, table_sel):
        """
        Parses the nutritional table into a dictionary.
        """
        nutri_dict = {}
        rows = table_sel.xpath(".//tbody/tr")
        for row in rows:
            cells = row.xpath("./td")
            if not cells:
                continue
            key = cells[0].xpath("string(.)").get("").strip()
            value_parts = []
            for cell in cells[1:]:
                val = cell.xpath("string(.)").get("").strip()
                if val:
                    value_parts.append(val)
            if key:
                nutri_dict[key] = " ".join(value_parts)
        return nutri_dict

    def extract_from_html(self, html_content):
        """
        Extracts specific text fields from the PDP HTML.
        """
        if not html_content:
            return {}
        
        sel = Selector(text=html_content)
        data = {}
        
        data['product_description'] = sel.xpath("string(//div[contains(@class, 'lib-product-description')])").get("").strip()
        data['notes'] = self.get_tab_content(sel, "Opombe").xpath("string(.)").get("").strip()
        data['ingredients'] = self.get_tab_content(sel, "Sestavine").xpath("string(.)").get("").strip()
        data['features'] = self.get_tab_content(sel, "Lastnosti").xpath("string(.)").get("").strip()
        data['instructionforuse'] = self.get_tab_content(sel, "Navodila za uporabo").xpath("string(.)").get("").strip()
        data['product_specific_data'] = self.get_tab_content(sel, "Podatki specifični za izdelek").xpath("string(.)").get("").strip()
        data['contact_address'] = self.get_tab_content(sel, "Kontaktni naslov").xpath("string(.)").get("").strip()
        
        nutri_table = self.get_tab_content(sel, "Hranilne vrednosti").xpath(".//table")
        if nutri_table:
            data['nutritional_values'] = self.parse_nutritional_table(nutri_table)
        else:
            data['nutritional_values'] = {}
            
        return data

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            pdp_url = doc.get("pdp_url")
            nested_data = doc.get("data", {})
            
            # unique_id : itemId
            unique_id = nested_data.get("itemId") or doc.get("itemId") or doc.get("product_id")
            if not unique_id:
                logger.warning(f"Item {idx}/{total} has no ID. Skipping.")
                continue

            unique_id = str(unique_id)

            # De-duplicate
            if self.product_collection.find_one({"unique_id": unique_id}):
                logger.debug(f"Skipped already parsed: {unique_id}")
                continue

            logger.info(f"Processing Item {idx}/{total}: {unique_id}")
            
            # 1. Fetch live HTML for specific fields
            full_url = pdp_url if pdp_url.startswith("http") else f"https://mercatoronline.si{pdp_url}"
            html_content = self.fetch_pdp_html(full_url)
            html_data = self.extract_from_html(html_content)

            # 2. Map fields strictly as requested
            item = {}
            item['unique_id'] = unique_id
            item['competitor_name'] = "mercator"
            item['extraction_date'] = EXTRACTION_DATE
            
            # product_name : name
            item['product_name'] = nested_data.get("name") or doc.get("name") or doc.get("short_name")
            
            # brand : brand_name
            item['brand'] = nested_data.get("brand_name")
            
            # grammage
            item['grammage_quantity'] = nested_data.get("unit_quantity")
            item['grammage_unit'] = nested_data.get("invoice_unit")
            
            # hierarchy
            item['producthierarchy_level1'] = " VSI IZDELKI "
            item['producthierarchy_level2'] = nested_data.get("category1", "")
            item['producthierarchy_level3'] = nested_data.get("category2", "")
            item['producthierarchy_level4'] = nested_data.get("category3", "")
            
            # Price Logic
            raw_normal_price = nested_data.get("normal_price")
            raw_current_price = nested_data.get("current_price")
            
            try:
                norm_p = float(raw_normal_price) if raw_normal_price else 0.0
                curr_p = float(raw_current_price) if raw_current_price else 0.0
            except:
                norm_p, curr_p = 0.0, 0.0

            if norm_p == 0:
                item['regular_price'] = f"{curr_p:.2f}"
                item['selling_price'] = f"{curr_p:.2f}"
                item['price_was'] = ""
            else:
                item['regular_price'] = f"{norm_p:.2f}"
                item['selling_price'] = f"{curr_p:.2f}"
                item['price_was'] = str(raw_normal_price)

            # promotion_valid_upto : offer_expires_on
            item['promotion_valid_upto'] = nested_data.get("offer_expires_on")
            
            # percentage_discount : discounts -> value
            discounts = nested_data.get("discounts", [])
            item['percentage_discount'] = discounts[0].get("value", "") if discounts else ""
            
            # price_per_unit : f"{price_per_unit}/{price_per_unit_base}"
            ppu = nested_data.get("price_per_unit")
            ppu_base = nested_data.get("price_per_unit_base")
            if ppu:
                try:
                    ppu_rounded = round(float(ppu), 2)
                    item['price_per_unit'] = f"{ppu_rounded}/{ppu_base}" if ppu_base else str(ppu_rounded)
                except:
                    item['price_per_unit'] = str(ppu)
            else:
                item['price_per_unit'] = ""

            item['currency'] = "EUR"
            
            # breadcrumb
            breadcrumb_parts = [item['producthierarchy_level1'], item['producthierarchy_level2'], item['producthierarchy_level3'], item['producthierarchy_level4']]
            item['breadcrumb'] = " > ".join([p for p in breadcrumb_parts if p])
            
            item['pdp_url'] = full_url
            
            # allergens : join hover_text starting with "Vsebuje"
            allergens_list = nested_data.get("allergens", [])
            vsebuje_allergens = [a.get("hover_text") for a in allergens_list if a.get("hover_text", "").startswith("Vsebuje")]
            item['allergens'] = ", ".join(vsebuje_allergens)
            
            # rating/review
            item['rating'] = nested_data.get("ratings_sum")
            item['review'] = nested_data.get("ratings_num")
            
            # image_url_1 : mainImageSrc
            item['image_url_1'] = doc.get("mainImageSrc")
            
            # site_shown_uom : name
            item['site_shown_uom'] = item['product_name']
            
            # product_unique_key : unique_id + P
            item['product_unique_key'] = f"{unique_id}P"
            
            # Merge fields from HTML extraction
            item.update(html_data)

            # 3. Save to MongoDB
            try:
                product_item = ProductDataItem(**item)
                product_item.validate()
                self.product_collection.insert_one(item)
                logger.info(f"    Saved: {unique_id}")
            except Exception as e:
                logger.error(f"    Save error for {unique_id}: {e}")
            
            time.sleep(1) # Polite delay

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    parser_obj = Parser()
    try:
        parser_obj.start()
    finally:
        parser_obj.close()
