import json
import logging
import random
import time
import requests
import pymongo
from pymongo import MongoClient
from parsel import Selector

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

    def _clean(self, text):
        return " ".join(text.split()).strip() if text else ""

    def fetch_product_details(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"  Fetching {url} (Attempt {attempt + 1})...")
                response = requests.get(url, headers={**self.headers, 'referer': 'https://www.mrosupply.com/'}, timeout=30)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.error(f"    Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"    Failed [{response.status_code}] to fetch: {url}")
            
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
            
            html_content = self.fetch_product_details(pdp_url)
            
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
        sel = Selector(text=html_content)
        #XPATH
        MANUFACTURER_PART_NUMBER_XPATH = '//p[strong[normalize-space(text())="MODEL"]]/text()[normalize-space()]'
        UOI_XPATH = '//div[contains(@class,"flex-table--item")][.//p[contains(text(),"UOM")]]//div[contains(@class,"body")]//p/text()'
        UPC_XPATH = '//div[contains(@class,"flex-table--item")][.//p[contains(text(),"UPC")]]//div[contains(@class,"body")]//p/text()'
        


        # 1. JSON-LD Extraction
        ld = {}
        for raw in sel.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(raw)
                ld = data[0] if isinstance(data, list) else data
                if ld.get("@type") == "Product": break
            except: pass
        
        offers = ld.get('offers', {})
        if isinstance(offers, list): offers = offers[0] if offers else {}

        # 2. Extract Fields from JSON-LD and HTML
        manufacturer_part_number = str(offers.get("mpn") or \
            self._clean(sel.xpath(MANUFACTURER_PART_NUMBER_XPATH).get()) or "")
        
        vendor_seller_part_number = str(offers.get('sku') or "")
        item_name = str(offers.get('name') or "")
        price = str(offers.get('price') or "")
        
        brand_name = ld.get('brand', {}).get('name') if isinstance(ld.get('brand'), dict) else ld.get('brand')
        brand_name = str(brand_name or "")
        availability = str(offers.get('availability', '')).split('/')[-1]
        
        # UOM and UPC
        uoi = str(self._clean(sel.xpath(UOI_XPATH).get()) or "")
        upc = str(self._clean(sel.xpath(UPC_XPATH).get()) or "")

        # full_product_description
        desc_dict = {}
        body = sel.xpath('//div[@id="additionalDescription"]//div[contains(@class,"body")]')
        
        h5_texts = body.xpath('.//h5//text()').getall()
        if h5_texts:
            intro = self._clean(h5_texts[0])
            if intro and len(intro) > 30 and "Key Features" not in intro:
                desc_dict["Description"] = intro

        # Extract from tables
        for tr in body.xpath('.//table//tr'):
            cells = tr.xpath('./th | ./td')
            if len(cells) >= 2:
                k = self._clean(" ".join(cells[0].xpath('.//text()').getall()))
                v = self._clean(" ".join(cells[-1].xpath('.//text()').getall()))
                if k: desc_dict[k] = v
                
        # Extract from bullet lists
        for li in body.xpath('.//ul/li | .//ol/li'):
            text = self._clean(" ".join(li.xpath('.//text()').getall()))
            if text and ":" in text:
                parts = text.split(":", 1)
                k, v = self._clean(parts[0]), self._clean(parts[1])
                if k and v: desc_dict[k] = v
        
        full_product_description = json.dumps(desc_dict)

        # full_product_description_2 (Specifications)
        specs_dict = {
            self._clean(i.xpath('.//p[contains(@class,"key")]//text()').get()): 
            self._clean(" ".join(i.xpath('.//p[contains(@class,"value")]//text()').getall()))
            for i in sel.xpath('//div[contains(@class,"m-accordion--item")][.//p[text()="SPECIFICATION"]]//div[contains(@class,"o-grid-item")]')
        }
        full_product_description_2 = json.dumps(specs_dict)

        # Category breadcrumbs
        breadcrumbs = [self._clean(c) for c in (sel.xpath('//nav[contains(@class,"breadcrumb")]//a//text()').getall() or sel.xpath('//*[contains(@class,"breadcrumb")]//a//text()').getall())]
        category = " > ".join([c for c in breadcrumbs if c and c.lower() != 'home'])

        # Build final item
        item = {
            'company_name':'MROSupply',
            'manufacturer_name': brand_name,
            'brand_name': brand_name,
            'manufacturer_part_number': manufacturer_part_number,
            'vendor_seller_part_number': vendor_seller_part_number,
            'item_name': item_name,
            'full_product_description': full_product_description,
            'full_product_description_2': full_product_description_2,
            'price': price,
            'country_of_origin': "",
            'unit_of_issue': uoi,
            'qty_per_uoi': "1", 
            'upc': upc,
            'model_number': "",
            'product_category': category,
            'url': pdp_url,
            'availability': availability,
            'date_crawled': EXTRACTION_DATE,
            'lead_time': "",
            'rohs_reach': "",
            'stock_on_hand': ""
        }

        try:
            # Validate and Save
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
