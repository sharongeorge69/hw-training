import json
import time
import random
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB, MONGO_RAW_RESPONSE_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_RAW_RESPONSE, MONGO_COLLECTION_URL_FAILED,
    headers, EXTRACTION_DATE
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
        self.headers = headers
        
        # PyMongo connections
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.raw_db = self.client[MONGO_RAW_RESPONSE_DB]
        
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.raw_collection = self.raw_db[MONGO_COLLECTION_RAW_RESPONSE]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        
        # Create unique indexes
        self.product_collection.create_index("product_page_url", unique=True)
        self.raw_collection.create_index("product_page_url", unique=True)
        logger.info("Connected to MongoDB")

    def fetch_product_details(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=20)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.error(f"  Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"  Failed [{response.status_code}] to fetch: {url} (Attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"  Error on attempt {attempt + 1} for {url}: {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = (2 ** (attempt + 1)) + random.uniform(0, 1)
                time.sleep(wait_time)
        return None

    def start(self):
        total_urls = self.url_collection.count_documents({})
        logger.info(f"Total PDP URLs to process: {total_urls}")

        for index, document in enumerate(self.url_collection.find(), 1):
            pdp_url = document.get("pdp_url")
            
            # Skip if already parsed
            if self.product_collection.find_one({"product_page_url": pdp_url}):
                continue

            logger.info(f"Processing Item {index}/{total_urls}: {pdp_url}")
            
            html_content = self.fetch_product_details(pdp_url)
            
            if not html_content:
                logger.error(f"Failed to fetch content for: {pdp_url}")
                self.failed_url_collection.update_one(
                    {"product_page_url": pdp_url},
                    {"$set": document},
                    upsert=True
                )
                continue

            self.parse_item(pdp_url, html_content)

    def parse_item(self, pdp_url, html_content):
        try:
            selector = Selector(text=html_content)
            script_text = selector.xpath("//script[@id='ssr-pwa-state']/text()").get()
            
            if not script_text:
                logger.error(f"  Could not find ssr-pwa-state for: {pdp_url}")
                return

            # Replace custom encoding &q; with "
            json_str = script_text.replace('&q;', '"')
            data = json.loads(json_str)
            
            # Find the product data key
            product_key = next((k for k in data.keys() if str(k).startswith("product-")), None)
            if not product_key:
                logger.error(f"  Product key missing in JSON for: {pdp_url}")
                return
            
            product_data = data[product_key].get("data", {})
            product_group = product_data.get("productGroup", {})
            
            # Field Extraction
            pdp_name = product_group.get("productName")
            brand_name = product_group.get("productBrandDetails", {}).get("brandName")
            
            raw_specs = product_group.get("productAttributes", {})
            pdp_specs = {}
            if brand_name:
                pdp_specs["Brand"] = brand_name
            
            for key, val in raw_specs.items():
                if isinstance(val, list) and len(val) == 1:
                    pdp_specs[key] = val[0]
                else:
                    pdp_specs[key] = val

            pdp_desc = product_group.get("productDescripton")
            pdp_features_list = product_group.get("productKeyFeatures", [])
            pdp_images_raw = product_group.get("productAllImages", [])
            #product_features
            pdp_features = ", ".join(pdp_features_list) if isinstance(pdp_features_list, list) else str(pdp_features_list)

            image_urls = []
            for img in pdp_images_raw:
                if isinstance(img, dict):
                    url_val = img.get("imageWebUrl") or img.get("imageUrl") or img.get("links", {}).get("xxlarge")
                    if url_val:
                        image_urls.append(f"https://cdn.moglix.com/{url_val}")
                else:
                    image_urls.append(f"https://cdn.moglix.com/{img}")
            pdp_image_url = ", ".join(image_urls)

            # Construct Item
            item = {}
            item["product_page_url"] = pdp_url
            item["product_name"] = pdp_name
            item["product_specifications"] = json.dumps(pdp_specs)
            item["product_description"] = pdp_desc
            item["product_features"] = pdp_features
            item["product_image_url"] = pdp_image_url
            item["product_video_url"] = ""
            
            # Save Raw Response (Aldi standard)
            raw_doc = {
                "product_page_url": pdp_url,
                "html_content": html_content,
                "extraction_date": EXTRACTION_DATE
            }
            self.raw_collection.update_one(
                {"product_page_url": pdp_url},
                {"$set": raw_doc},
                upsert=True
            )

            # Save Parsed Data with validation
            validator = ProductDataItem(**item)
            validator.validate()
            self.product_collection.insert_one(item)
            logger.info(f"    Saved data for: {pdp_url}")

        except Exception as e:
            logger.error(f"  Critical parsing error for {pdp_url}: {e}")

    def close(self):
        try:
            self.client.close()
            logger.info("connection closed")
        except:
            pass

if __name__ == "__main__":
    moglix_parser = Parser()
    try:
        moglix_parser.start()
    finally:
        moglix_parser.close()
