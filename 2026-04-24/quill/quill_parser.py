import re
import json
import time
import random
import logging
import requests
import pymongo
from parsel import Selector
from pymongo import MongoClient

from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_URL_FAILED, EXTRACTION_DATE, TARGET_URLS, HEADERS
)
from items import ProductDataItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuillParser:
    def __init__(self):
        # Setup Session
        self.session = requests.Session()
        self.headers = HEADERS
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]

        # Unique index on url
        self.product_collection.create_index("url", unique=True)
        logger.info(f"Connected to MongoDB: {MONGO_DB}")

    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^\x20-\x7E]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def fetch_page(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                logger.info(f"  Fetching: {url} (Attempt {attempt + 1})")
                resp = self.session.get(url, headers=self.headers, timeout=30)

                if resp.status_code == 200:
                    if 'id="SEOSchemaJson"' not in resp.text:
                        logger.warning(f"  Invalid page content or Blocked: {url}")
                        continue
                    return resp.text
                elif resp.status_code == 404:
                    logger.error(f"  Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"  Failed [{resp.status_code}]: {url}")

            except Exception as e:
                logger.warning(f"  Error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                wait = 2 ** attempt + random.uniform(1, 2)
                time.sleep(wait)
        return None

    def parse_item(self, pdp_url, html_content):
        try:
            sel = Selector(text=html_content)

            # JSON-LD
            json_raw = sel.xpath('//script[@id="SEOSchemaJson"]/text()').extract_first()
            ld_data = json.loads(json_raw) if json_raw else {}
            offers = ld_data.get("offers", {})

            # Specification Dictionary (description_2)
            specification_dictionary = {}
            spec_rows = sel.xpath('//div[@id="skuSpecification"]//div[contains(@class, "col")]')
            current_key = None
            for div in spec_rows:
                key_text = "".join(div.xpath('.//span[@class="font-weight-bold"]/text()').extract()).strip()
                if key_text:
                    current_key = key_text
                else:
                    if current_key:
                        val_text = "".join(div.xpath('.//text()').extract()).strip()
                        specification_dictionary[current_key] = val_text
                        current_key = None

            # Fields
            brand_name = ld_data.get("brand", "")
            item_name = self.clean_text(ld_data.get("name", ""))
            manufacturer_part_number = ld_data.get("mpn", "")
            vendor_part_number = ld_data.get("sku", "")
            price = str(offers.get("price", ""))
            availability = offers.get("availability", "").split("/")[-1] if offers.get("availability") else "Instock"
            url_field = ld_data.get("URL", pdp_url)
            model_number = ld_data.get("model", "")

            # Description
            desc_nodes = sel.xpath('//div[@id="skuDescription"]//div[contains(@class, "qOverflow")]//text()[not(parent::script)]').extract()
            full_description = self.clean_text(" ".join(desc_nodes))

            # Product Category
            breadcrumbs = sel.xpath('//div[contains(@class, "scroll-breadcrumb")]//li/a/span/text()').extract()
            product_category = " > ".join(t.strip() for t in breadcrumbs if t.strip())

            # Unit of Issue & Qty per UOI
            uoi_raw = specification_dictionary.get("Selling Quantity (UOM)","") or sel.xpath('//div[contains(@class, "selling-uom")]/text()').extract_first("")
            unit_of_issue = uoi_raw.replace("Per", "") if "Per" in uoi_raw else uoi_raw
            qty_per_uoi = specification_dictionary.get("Pack Qty", "") or "1"

            item = {}
            item["company_name"] = "Quill"
            item["manufacturer_name"] = brand_name
            item["brand_name"] = brand_name
            item["manufacturer_part_number"] = manufacturer_part_number
            item["vendor_seller_part_number"] = vendor_part_number
            item["model_number"] = model_number
            item["item_name"] = item_name
            item["full_product_description"] = full_description
            item["price"] = price
            item["unit_of_issue"] = unit_of_issue
            item["qty_per_uoi"] = qty_per_uoi
            item["product_category"] = product_category
            item["url"] = url_field
            item["availability"] = availability
            item["date_crawled"] = EXTRACTION_DATE
            item["full_product_description_2"] = specification_dictionary  
            item["lead_time"] = ""
            item["rohs_reach"] = ""
            item["stock_on_hand"] = ""
            item["upc"] = ""
            item["country_of_origin"] = ""
            
          
            # Save to MongoDB
            try:
                # Validation
                ProductDataItem(**item).validate()
                self.product_collection.insert_one(item)
                logger.info(f"  Saved: {item['item_name']} ({pdp_url})")
            except pymongo.errors.DuplicateKeyError:
                logger.info(f"  Already exists (skipping): {pdp_url}")
            except Exception as e:
                logger.error(f"  Save error for {pdp_url}: {e}")

        except Exception as e:
            logger.error(f"  Error parsing {pdp_url}: {e}")

    def start(self):
        total = len(TARGET_URLS)
        logger.info(f"Starting Quill parser — {total} URLs")
        for idx, url in enumerate(TARGET_URLS, 1):
            logger.info(f"\nProcessing {idx}/{total}: {url}")
            html = self.fetch_page(url)
            if html:
                self.parse_item(url, html)
            else:
                self.failed_url_collection.update_one(
                    {"url": url},
                    {"$set": {"url": url, "date_crawled": EXTRACTION_DATE}},
                    upsert=True
                )
            time.sleep(random.uniform(1.5, 4.0))

    def close(self):
        self.client.close()

if __name__ == "__main__":
    parser = QuillParser()
    try:
        parser.start()
    finally:
        parser.close()
