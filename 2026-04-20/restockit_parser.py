import re
import pymongo
import time
import random
import json
import logging
from pymongo import MongoClient
from parsel import Selector
from camoufox.sync_api import Camoufox

from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, 
    MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED,
    headers, EXTRACTION_DATE
)
from items import ProductDataItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.headers = headers
        
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        
        # Create indexes
        self.product_collection.create_index("url", unique=True)
        logger.info("Connected to MongoDB")

    def extract_uoi_qty(self, text):
        if not text:
            return "", ""

        text = text.strip().lower()

        units = r'(cases?|cartons?|boxes|box|packs?|sets?|rolls?|bottles?|reams?|tubes?|kits?|gallons?|dozens?)'

        # Pattern 1: "6 sets of 10"
        match = re.search(rf'\d+\s*{units}\s*of\s*(\d+)', text)
        if match:
            uoi_match = re.search(units, match.group(0))
            uoi = uoi_match.group(1).capitalize() if uoi_match else ""
            qty = match.group(2)
            return uoi, qty

        # Pattern 2: "case of 9"
        match = re.search(rf'{units}\s*of\s*(\d+)', text)
        if match:
            return match.group(1).capitalize(), match.group(2)

        # Pattern 3: "2 rolls"
        match = re.search(rf'(\d+)\s*{units}', text)
        if match:
            return match.group(2).capitalize(), match.group(1)

        # Pattern 4: each
        if "each" in text:
            return "Each", "1"

        return text.capitalize(), ""

    def fetch_product_details(self, page, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"  Navigating to {url} (Attempt {attempt + 1})...")
                response = page.goto(url, wait_until="load", timeout=60000)
                
                if response and response.status == 200:
                    # Give dynamic content time to load
                    time.sleep(2)
                    return page.content()
                elif response and response.status == 404:
                    logger.error(f"    Product not found (404): {url}")
                    return None
                else:
                    status = response.status if response else "No Response"
                    logger.error(f"    Failed [{status}] to fetch: {url}")
            
            except Exception as e:
                logger.warning(f"    Retryable error for {url} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                logger.error(f"    Max retries reached for: {url}")
        
        return None

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        with Camoufox(headless=True) as browser:
            page = browser.new_page()
            
            for idx, doc in enumerate(self.url_collection.find(), 1):
                pdp_url = doc.get("pdp_url")
                
                if not pdp_url:
                    logger.warning(f"Item {idx}/{total} is missing URL. Skipping.")
                    continue

                # De-duplicate using URL
                if self.product_collection.find_one({"url": pdp_url}):
                    logger.info(f"Processing Item {idx}/{total}: {pdp_url} (Already parsed, skipping)")
                    continue

                logger.info(f"Processing Item {idx}/{total}: {pdp_url}")
                
                html_content = self.fetch_product_details(page, pdp_url)
                
                if not html_content:
                    logger.error(f"    Skipping {pdp_url} because fetching failed.")
                    self.failed_url_collection.update_one(
                        {"url": pdp_url},
                        {"$set": doc},
                        upsert=True
                    )
                    continue

                self.parse_item(pdp_url, html_content)

    def parse_item(self, pdp_url, html_content):
        selector = Selector(text=html_content)
        
        # Standard XPaths
        BREADCRUMBS_XPATH = '//a[contains(@class, "breadcrumbs__link")]/text()'
        UPC_XPATH = '//div[contains(@class, "mt-3") and contains(strong, "UPC")]/text()[normalize-space()]'
        INVENTORY_SCRIPT_XPATH = '//script[@data-product-inventory-json]/text()'
        JSON_LD_XPATH = '//script[@type="application/ld+json"]/text()'
        COUNTRY_OF_ORIGIN_XPATH = '//*[local-name()="tr"][.//td[normalize-space(.)="Country of Origin"]]/td[last()]/text()'
        CASE_PACK_XPATH = '//*[local-name()="tr"][.//td[normalize-space(.)="Case Pack"]]/td[last()]/text()'
        CASE_PACK_XPATH_2 = 'normalize-space(substring-after(//span[@data-price], "/"))'
        # 1. JSON-LD Extraction
        json_ld_data = {}
        json_ld_scripts = selector.xpath(JSON_LD_XPATH).getall()
        for script in json_ld_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, list):
                    for ld_item in data:
                        if ld_item.get("@type") == "Product":
                            json_ld_data = ld_item
                elif data.get("@type") == "Product":
                    json_ld_data = data
            except:
                continue
        #item name
        item_name = json_ld_data.get('name', '')
        item_name = item_name.strip() if item_name else ""
        #brand name
        brand_name = json_ld_data.get('brand', {}).get('name', '')
        brand_name = brand_name.strip() if brand_name else ""
        #manufacturer name
        manufacturer_name = brand_name

        #vendor seller part number
        vendor_seller_part_number = json_ld_data.get('sku', '')
        #price
        offers = json_ld_data.get('offers', {})
        if isinstance(offers, list):
            price_val = offers[0].get('price', '')
        else:
            price_val = offers.get('price', '')
        price = str(price_val)
        #description
        description = json_ld_data.get('description', '')
        description = ' '.join(description.split()) if description else ""
        #categories
        categories = selector.xpath(BREADCRUMBS_XPATH).getall()
        categories = [c.strip() for c in categories if c.strip().lower() not in ['home', '/']]
        product_category = " > ".join(categories)

        #upc
        upc = selector.xpath(UPC_XPATH).get()
        if upc:
            upc = upc.strip()
        else:
            upc_match = re.search(r'"barcode"\s*:\s*"(\d{12,13})"', html_content)
            if upc_match:
                upc = upc_match.group(1).strip()

        #stock on hand and availability
        stock_on_hand = ""
        availability = ""
        inventory_script = selector.xpath(INVENTORY_SCRIPT_XPATH).get()
        if inventory_script:
            try:
                inventory_data = json.loads(inventory_script)
                inventory_items = inventory_data.get('inventory', {})
                if inventory_items:
                    first_variant = list(inventory_items.values())[0]
                    stock_on_hand = str(first_variant.get('inventory_quantity', ''))
                    availability = first_variant.get('inventory_message', '')

            except:
                pass

        raw_uoi = selector.xpath(CASE_PACK_XPATH).get()
        if raw_uoi == None:
            raw_uoi = selector.xpath(CASE_PACK_XPATH_2).get()
        
        parsed_uoi, parsed_qty = self.extract_uoi_qty(raw_uoi)
        
        country_of_origin = selector.xpath(COUNTRY_OF_ORIGIN_XPATH).get()
        country_of_origin = country_of_origin.strip() if country_of_origin else ""

        item = {}
        item['company_name'] = 'Restockit'
        item['manufacturer_name'] = manufacturer_name
        item['brand_name'] = brand_name
        item['vendor_seller_part_number'] = vendor_seller_part_number
        item['item_name'] = item_name
        item['full_product_description'] = description
        item['price'] = price
        item['unit_of_issue'] = parsed_uoi
        item['qty_per_uoi'] = parsed_qty
        item['upc'] = upc
        item['product_category'] = product_category
        item['url'] = pdp_url
        item['availability'] = availability
        item['date_crawled'] = EXTRACTION_DATE
        item['stock_on_hand'] = stock_on_hand
        item['lead_time'] = ""
        item['rohs_reach'] = ""
        item['model_number'] = ""
        item['manufacturer_part_number'] = ""
        item['country_of_origin'] = country_of_origin


        try:
            # Schema validation and save
            product_item = ProductDataItem(**item)
            product_item.validate()
            self.product_collection.insert_one(item)
            logger.info(f"    Saved: {pdp_url}")
            
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"    Skipped duplicate: {pdp_url}")
        except Exception as e:
            logger.error(f"    Save error for {pdp_url}: {e}")

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
