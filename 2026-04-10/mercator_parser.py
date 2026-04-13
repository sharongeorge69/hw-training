import re
import time
import random
import requests
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

    def extract_grammage(self, name, unit_quantity, invoice_unit):
        """
        Core extraction logic with refined priority and multipack string preservation.
        """
        name = str(name).lower()
        
        # RULE 1: Multipack pattern (e.g., 4 x 125 g, 6 x 1 l)
        multi_match = re.search(r'(\d+)\s?[x*]\s?(\d+(?:[.,]\d+)?)\s?(kg|g|ml|l)\b', name)
        if multi_match:
            count = multi_match.group(1)
            val = multi_match.group(2).replace(',', '.')
            unit = multi_match.group(3)
            return f"{count} x {val}", unit.lower()
        
        # RULE 2: Simple Grammage (e.g., 400 g, 1 l)
        grammage_match = re.search(r'(\d+(?:[.,]\d+)?)\s?(kg|g|ml|l)\b', name)
        if grammage_match:
            qty = grammage_match.group(1).replace(',', '.')
            unit = grammage_match.group(2)
            return qty, unit.lower()

        # RULE 3/4: Ignore dimensions or pack patterns -> return 1 kos
        if re.search(r'\d+\s?(mm|cm|m)\s?x\s?\d+', name) or re.search(r'\d+/\d+', name):
            return 1, "kos"
        
        # Fallback to API data, ensuring lowercase unit
        final_unit = str(invoice_unit).lower()
        return unit_quantity, final_unit

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
            
            # EXTRACT
            key = cells[0].xpath("string(.)").extract_first("").strip()
            value_parts = []
            for cell in cells[1:]:
                val = cell.xpath("string(.)").extract_first("").strip()
                if val:
                    value_parts.append(val)
            if key:
                nutri_dict[key] = " ".join(value_parts)
        return nutri_dict

    def get_pdp_data(self, url):
        """
        Fetches the PDP HTML with retries and extracts data fields.
        """
        max_retries = 3
        html_content = None
        
        # --- 1. FETCHING ---
        for attempt in range(max_retries):
            try:                
                resp = requests.get(url, headers=self.headers, timeout=20)
                if resp.status_code == 200:
                    html_content = resp.text
                    break
                elif resp.status_code == 404:
                    logger.error(f"  Product not found (404): {url}")
                    return {}
            except Exception as e:
                logger.warning(f"  Retryable error for {url}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 + random.uniform(0, 1))
        
        if not html_content:
            return {}

        # --- 2. EXTRACTION ---
        sel = Selector(text=html_content)
        data = {}
        
        # XPATH
        PRODUCT_DESCRIPTION_XPATH = "string(//div[contains(@class, 'lib-product-description')])"
        
        # Tab content base XPath helper
        TAB_BASE_XPATH = "//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[contains(normalize-space(), '{}')]/@href, '#')]"
        
        NOTES_XPATH = f"string({TAB_BASE_XPATH.format('Opombe')})"
        INGREDIENTS_XPATH = f"string({TAB_BASE_XPATH.format('Sestavine')})"
        FEATURES_XPATH = f"string({TAB_BASE_XPATH.format('Lastnosti')})"
        INSTRUCTIONS_XPATH = f"string({TAB_BASE_XPATH.format('Navodila za uporabo')})"
        SPECIFIC_DATA_XPATH = f"string({TAB_BASE_XPATH.format('Podatki specifični za izdelek')})"
        DISTRIBUTOR_XPATH = f"string({TAB_BASE_XPATH.format('Kontaktni naslov')})"
        NUTRI_TABLE_XPATH = f"{TAB_BASE_XPATH.format('Hranilne vrednosti')}//table"

        # EXTRACT
        data['product_description'] = sel.xpath(PRODUCT_DESCRIPTION_XPATH).extract_first("").strip()
        data['notes'] = sel.xpath(NOTES_XPATH).extract_first("").strip()
        data['ingredients'] = sel.xpath(INGREDIENTS_XPATH).extract_first("").strip()
        data['features'] = sel.xpath(FEATURES_XPATH).extract_first("").strip()
        data['instructionforuse'] = sel.xpath(INSTRUCTIONS_XPATH).extract_first("").strip()
        data['product_specific_data'] = sel.xpath(SPECIFIC_DATA_XPATH).extract_first("").strip()
        data['distributor_address'] = sel.xpath(DISTRIBUTOR_XPATH).extract_first("").strip()
        
        nutri_table_sel = sel.xpath(NUTRI_TABLE_XPATH)
        if nutri_table_sel:
            data['nutritional_values'] = self.parse_nutritional_table(nutri_table_sel[0])
        else:
            data['nutritional_values'] = {}
            
        return data

    def parse_item(self, doc, idx, total):
        pdp_url = doc.get("pdp_url")
        nested_data = doc.get("data", {})
        
        # Determine unique_id
        unique_id = nested_data.get("itemId") or doc.get("itemId") or doc.get("product_id")
        if not unique_id:
            logger.warning(f"Item {idx}/{total} has no ID. Skipping.")
            return

        unique_id = str(unique_id)

        # De-duplicate
        if self.product_collection.find_one({"unique_id": unique_id}):
            logger.debug(f"Skipped already parsed: {unique_id}")
            return

        logger.info(f"Processing Item {idx}/{total}: {unique_id}")
        
        # 1. Scrape PDP data (fetch + extract)
        full_url = pdp_url if pdp_url.startswith("http") else f"https://mercatoronline.si{pdp_url}"
        html_data = self.get_pdp_data(full_url)

        product_name = nested_data.get("name") or doc.get("name") or doc.get("short_name")
        brand = nested_data.get("brand_name")
        
        # Refined grammage extraction
        raw_qty = nested_data.get("unit_quantity")
        raw_unit = nested_data.get("invoice_unit")
        grammage_quantity, grammage_unit = self.extract_grammage(product_name, raw_qty, raw_unit)
        
        hierarchy_level1 = " VSI IZDELKI "
        hierarchy_level2 = nested_data.get("category1", "")
        hierarchy_level3 = nested_data.get("category2", "")
        hierarchy_level4 = nested_data.get("category3", "")
        
        # Price Logic
        raw_normal_price = nested_data.get("normal_price")
        raw_current_price = nested_data.get("current_price")
        
        regular_price = ""
        selling_price = ""
        price_was = ""

        if raw_current_price:
            try:
                current_val = float(raw_current_price)
                selling_price = f"{current_val:.2f}"
                
                if raw_normal_price and float(raw_normal_price) != 0 and float(raw_normal_price) != current_val:
                    regular_price = f"{float(raw_normal_price):.2f}"
                    price_was = str(raw_normal_price)
                else:
                    regular_price = selling_price
            except:
                pass
            

        promotion_valid_upto = nested_data.get("offer_expires_on")
        
        # percentage_discount
        discounts = nested_data.get("discounts", [])
        percentage_discount = discounts[0].get("value", "") if discounts else ""
        
        # price_per_unit
        ppu = nested_data.get("price_per_unit")
        ppu_base = nested_data.get("price_per_unit_base")
        if ppu:
            try:
                ppu_rounded = round(float(ppu), 2)
                price_per_unit = f"{ppu_rounded}/{ppu_base}" if ppu_base else str(ppu_rounded)
            except:
                price_per_unit = str(ppu)
        else:
            price_per_unit = ""

        currency = "EUR"
        
        # breadcrumb
        breadcrumb_parts = [hierarchy_level1, hierarchy_level2, hierarchy_level3, hierarchy_level4]
        breadcrumb = " > ".join([p for p in breadcrumb_parts if p])
        
        # allergens
        allergens_list = nested_data.get("allergens", [])
        vsebuje_allergens = [a.get("hover_text") for a in allergens_list if a.get("hover_text") and isinstance(a.get("hover_text"), str) and a.get("hover_text").startswith("Vsebuje")]
        allergens = ", ".join(vsebuje_allergens)
        
        rating = nested_data.get("rating")
        review = nested_data.get("ratings_num")
        image_url_1 = doc.get("mainImageSrc")
        site_shown_uom = product_name
        product_unique_key = f"{unique_id}P"

        item = {}
        item['unique_id'] = unique_id
        item['competitor_name'] = "mercator"
        item['extraction_date'] = EXTRACTION_DATE
        item['product_name'] = product_name
        item['brand'] = brand
        item['grammage_quantity'] = grammage_quantity
        item['grammage_unit'] = grammage_unit
        item['producthierarchy_level1'] = hierarchy_level1
        item['producthierarchy_level2'] = hierarchy_level2
        item['producthierarchy_level3'] = hierarchy_level3
        item['producthierarchy_level4'] = hierarchy_level4
        item['regular_price'] = regular_price
        item['selling_price'] = selling_price
        item['price_was'] = price_was
        item['promotion_valid_upto'] = promotion_valid_upto
        item['percentage_discount'] = percentage_discount
        item['price_per_unit'] = price_per_unit
        item['currency'] = currency
        item['breadcrumb'] = breadcrumb
        item['pdp_url'] = full_url
        item['allergens'] = allergens
        item['rating'] = rating
        item['review'] = review
        item['image_url_1'] = image_url_1
        item['site_shown_uom'] = site_shown_uom
        item['product_unique_key'] = product_unique_key
        
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

    def start(self):
        """
        Iterates over the URL collection and processes each item.
        """
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            self.parse_item(doc, idx, total)

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
