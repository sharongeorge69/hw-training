import time
import random
import requests
import pymongo
import json
import re
import html
from pymongo import MongoClient
from datetime import datetime
import logging
from items import ProductDataItem
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_URL_FAILED,
    headers
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_description(text):
    if not text:
        return ""
    
    # Remove Disclaimer and everything after it
    text = re.split(r'(?i)<b>Disclaimer</b>|Disclaimer\b', text)[0]
    
    # Remove promotional text
    promo_text_pattern = r'(?i)So,?\s*what are you waiting for\?\s*Go ahead and buy this product online today!'
    text = re.sub(promo_text_pattern, '', text)
    
    # Remove all HTML tags (including img)
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Collapse multiple spaces and newlines into a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

class Parser:
    def __init__(self):
        self.headers = headers
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        
        # Create indexes
        self.product_collection.create_index("product_url", unique=True)
        logger.info("Connected to MongoDB")

    def fetch_api(self, url, headers):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 404:
                    logger.error(f"  Not found (404): {url}")
                    return None
                else:
                    logger.error(f"  Failed [{resp.status_code}] to fetch: {url} (Attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"  Retryable error for {url} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 * (attempt + 1) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                logger.error(f"  Max retries reached for: {url}")
        
        return None

    def fetch_price_api(self, slug, size):
        url = "https://www.jiomart.com/api/service/application/catalog/v1.0/products/sizes/price"
        json_data = {
            "items": [
                {
                    "slug": slug,
                    "size": size,
                }
            ]
        }
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=self.headers, json=json_data, timeout=20)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 404:
                    return None
            except Exception as e:
                logger.warning(f"  Retryable error for price API {slug} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 * (attempt + 1) + random.uniform(0, 1)
                time.sleep(wait_time)
        return None

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            slug = doc.get("slug")
            product_url = doc.get("product_url")
            
            if not slug or not product_url:
                logger.warning(f"Item {idx}/{total} is missing data. Skipping.")
                continue

            if self.product_collection.find_one({"product_url": product_url}):
                logger.debug(f"Skipped already parsed: {product_url}")
                continue

            logger.info(f"Processing Item {idx}/{total}: {slug}")
            
            api_url = f"https://www.jiomart.com/api/service/application/catalog/v1.0/products/{slug}"
            data = self.fetch_api(api_url, self.headers)
            
            if not data:
                logger.error(f"Skipping {slug} because fetching failed.")
                self.failed_url_collection.update_one(
                    {"product_url": product_url},
                    {"$set": doc},
                    upsert=True
                )
                continue

            self.parse_item(doc, data)

    def parse_item(self, doc, data):
        product_url = doc.get("product_url")
        slug = doc.get("slug")
        sizes = doc.get("sizes", [])
        size = sizes[0] if sizes else "OS"
        price_data = self.fetch_price_api(slug, size)
        
        # Default initialization to avoid UnboundLocalError
        product_availability = ""
        store_id = ""
        pincode = ""
        discount_percentage = ""
        quantity = 0
        product_rating = ""

        if price_data and "items" in price_data and price_data["items"]:
            price_item = price_data["items"][0]
            if "error" in price_item:
                product_availability = "Out of Stock"
            else:
                product_availability = "In Stock"
                store_id = str(price_item.get("store", {}).get("uid", ""))
                pincode = str(price_item.get("pincode", ""))
                discount_percentage = re.sub(r"[^\d.]", "", str(price_item.get("discount", "")))
                quantity = int(price_item.get("quantity", 0))

        # New parsed fields
        attributes = data.get("attributes", {})
        if isinstance(attributes, str):
            try:
                attributes = json.loads(attributes)
            except:
                attributes = {}
        item = {}
        review_code = attributes.get("group-product-id", "")

        if review_code:
            rating_url = f"https://www.jiomart.com/ext/jcp-jiomart/application/v1.0/op/review/product-statistics/{review_code}"
            rating_data = self.fetch_api(rating_url, self.headers)
            if rating_data:
                product_rating = str(rating_data.get("data", {}).get("averageRating", ""))
        # Fields from Mongo
        item["product_url"] = product_url
        item["product_id"] = doc.get("product_id")
        item["product_name"] = doc.get("product_name")
        item["brand"] = doc.get("brand")
        item["taxonomy"] = doc.get("taxonomy")
        item["category_name"] = doc.get("category_name")
        item["selling_price"] = doc.get("selling_price")
        item["mrp"] = doc.get("mrp")
        item["main_image_url"] = doc.get("main_image_url")
        item["image_urls"] = doc.get("image_urls")
        item["discount_percentage"] = discount_percentage
        item["product_availability"] = product_availability
        item["store_id"] = store_id
        item["pincode"] = pincode
        item["product_description"] = clean_description(data.get("description", ""))
        item["instructions"] = ""
        item["storage_instructions"] = ""
        item["stock_count"] = str(quantity)
        item["promotion_description"] = ""
        item["product_rating"] = product_rating
        item["extraction_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item["highlights"] =  ""
       

        try:
            product_item = ProductDataItem(**item)
            product_item.validate()
            self.product_collection.insert_one(item)
            logger.info(f"    Saved: {slug}")
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"    Skipped duplicate: {slug}")
        except Exception as e:
            logger.error(f"    Save error for {slug}: {e}")

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
