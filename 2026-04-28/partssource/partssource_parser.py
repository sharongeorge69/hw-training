import re
import json
import time
import random
import logging
from datetime import datetime
from curl_cffi import requests
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB, MONGO_RAW_RESPONSE_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_RAW_RESPONSE, MONGO_COLLECTION_URL_FAILED,
    headers, PROXIES_LIST, EXTRACTION_DATE
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
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.raw_db = self.client[MONGO_RAW_RESPONSE_DB]
        
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.raw_collection = self.raw_db[MONGO_COLLECTION_RAW_RESPONSE]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        
        # Create indexes
        self.product_collection.create_index("url", unique=True)
        self.raw_collection.create_index("url", unique=True)
        logger.info("Connected to MongoDB")

    def get_proxy(self):
        proxy_url = random.choice(PROXIES_LIST)
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def fetch_pdp(self, url):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                proxies = self.get_proxy()
                res = requests.get(
                    url, 
                    headers=headers, 
                    impersonate="chrome120", 
                    proxies=proxies, 
                    timeout=30
                )
                if res.status_code == 200:
                    return res.text
                elif res.status_code == 403:
                    logger.warning(f"  Forbidden (403) for {url}. Proxy might be blocked. Attempt {attempt + 1}")
                elif res.status_code == 404:
                    logger.error(f"  Not Found (404): {url}")
                    return None
            except Exception as e:
                logger.warning(f"  Error fetching {url} (Attempt {attempt + 1}): {e}")
            
            time.sleep(random.uniform(2, 5))
        return None

    def parse_item(self, url, html_content):
        try:
            pattern = r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*(?:\n\s*window\.|</script>)'
            match = re.search(pattern, html_content, re.DOTALL)
            if not match:
                logger.error(f"  Preloaded state not found for {url}")
                return None

            json_str = match.group(1).strip()
            if json_str.endswith(';'): json_str = json_str[:-1]
            data = json.loads(json_str)

            current_product_data = data.get("currentProduct", {})
            product = current_product_data.get("product", {})
            option = current_product_data.get("selectedOption", {})
            
            # Extract Attributes
            all_attributes = []
            attr_sources = [
                product.get("productAttributes"),
                option.get("attributes"),
                product.get("attributes") if isinstance(product.get("attributes"), list) else None
            ]
            for source in attr_sources:
                if isinstance(source, list):
                    all_attributes.extend(source)
            
            if not all_attributes:
                raw_str = product.get("attributes")
                if isinstance(raw_str, str):
                    parts = raw_str.split('|')
                    for part in parts:
                        if '~' in part:
                            s = part.split('~')
                            if len(s) >= 3:
                                all_attributes.append({"name": s[0], "value": s[1], "purpose": s[2]})

            features_list = []
            tech_spec_keys = {}
            for attr in all_attributes:
                if not isinstance(attr, dict): continue
                purpose = str(attr.get("purpose", "")).upper()
                name = str(attr.get("name", ""))
                value = attr.get("value")

                if purpose == "FEATURE":
                    if value: features_list.append(str(value).strip())
                elif purpose in ["TECHNICAL SPEC", "DIFFERENTIATING ATTRIBUTE"]:
                    clean_key = name.lower().strip().replace(" ", "_").replace("/", "_").replace("-", "_")
                    if clean_key == "materials" and isinstance(value, str) and "," in value:
                        value = [v.strip() for v in value.split(",")]
                    tech_spec_keys[clean_key] = value

            tech_spec_base = {
                "item": product.get("title"),
                "oem": product.get("manufacturer"),
                "oem_number": product.get("displayPartNumber"),
                "condition": "New OEM Original",
                "returnable": option.get("isReturnable") if option.get("isReturnable") is not None else "No",
                "warranty": "Mfr Warranty"
            }
            tech_spec_base.update(tech_spec_keys)

            item = {
                "manufacturer_name": product.get("manufacturer"),
                "brand_name": product.get("manufacturer"),
                "manufacturer_part_number": product.get("displayPartNumber"),
                "vendor_seller_part_number": option.get("vendorItemNumber"),
                "item_name": product.get("title"),
                "product_overview": product.get("productOverview", ""),
                "features": " ".join(features_list),
                "technical_spec": json.dumps(tech_spec_base, indent=4),
                "product_category": " > ".join(product.get("categories", [])) if isinstance(product.get("categories"), list) else product.get("categories"),
                "upc": tech_spec_keys.get("upc_code", ""),
                "country_of_origin": tech_spec_keys.get("country_of_origin", ""),
                "price": str(option.get("price") or product.get("price")),
                "unit_of_issue": option.get("unitOfMeasurement"),
                "qty_per_uoi": str(tech_spec_keys.get("package_quantity", "")),
                "stock_on_hand": str(option.get("inventory")),
                "lead_time": option.get("estimatedShipMessage"),
                "url": url,
                "availability": "In Stock" if product.get("availability") else "Out of Stock",
                "date_crawled": EXTRACTION_DATE
            }
            return item

        except Exception as e:
            logger.error(f"  Error parsing {url}: {e}")
            return None

    def save_raw_response(self, url, html_content):
        try:
            raw_item = {
                "url": url,
                "html_content": html_content,
                "extraction_date": datetime.now().strftime("%Y-%m-%d")
            }
            self.raw_collection.update_one(
                {"url": url},
                {"$set": raw_item},
                upsert=True
            )
        except Exception as e:
            logger.error(f"  Error saving raw response for {url}: {e}")

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total URLs to process: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            url = doc.get("pdp_url")
            if not url:
                continue

            if self.product_collection.find_one({"url": url}):
                logger.info(f"[{idx}/{total}] Already processed: {url}")
                continue

            logger.info(f"[{idx}/{total}] Processing: {url}")
            html_content = self.fetch_pdp(url)
            
            if not html_content:
                logger.error(f"  Request failed for {url}")
                self.failed_url_collection.update_one(
                    {"url": url},
                    {"$set": {"url": url, "failed_at": datetime.now()}},
                    upsert=True
                )
                continue

            # Save raw response
            self.save_raw_response(url, html_content)

            # Parse and save
            item_data = self.parse_item(url, html_content)
            if item_data:
                try:
                    product_item = ProductDataItem(**item_data)
                    # For MongoEngine to save to the collection defined in meta
                    self.product_collection.insert_one(item_data)
                    logger.info(f"  Saved product data for {url}")
                except Exception as e:
                    logger.error(f"  Error saving product data for {url}: {e}")
            
            # Etiquette delay
            time.sleep(random.uniform(1, 3))

    def close(self):
        self.client.close()
        logger.info("MongoDB connection closed")

if __name__ == "__main__":
    parser = Parser()
    try:
        parser.start()
    finally:
        parser.close()
