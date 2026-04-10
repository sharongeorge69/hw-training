import logging
import time
import requests
from parsel import Selector
import re
from pymongo import MongoClient
import pymongo
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, HEADERS_API, HEADERS_HTML
from items import ResponseURLItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.headers_api = HEADERS_API
        self.headers_html = HEADERS_HTML
        self.base_url = 'https://mercatoronline.si/products/browseProducts/getProducts'
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        
        # Create unique index to avoid duplicates
        self.url_collection.create_index("pdp_url", unique=True)
        logger.info("Connected to MongoDB")

        # Categories will be populated dynamically
        self.categories = {}

    def get_timestamp(self):
        return int(time.time() * 1000)

    def get_categories(self):
        logger.info("Fetching categories from site...")
        try:
            response = requests.get('https://mercatoronline.si/brskaj', headers=self.headers_html, timeout=20)
            if response.status_code == 200:
                sel = Selector(text=response.text)
                category_names = sel.xpath('//li[contains(@class, "lib-category-menu-top")]/a/@data-analytics-label').getall()
                category_ids = sel.xpath('//li[contains(@class, "lib-category-menu-top")]/@data-category-id').getall()
                
                if category_names and category_ids and len(category_names) == len(category_ids):
                    self.categories = dict(zip(category_names, category_ids))
                    logger.info(f"Successfully fetched {len(self.categories)} categories.")
                    return True
                else:
                    logger.error("Failed to parse categories or mismatch in names/ids count.")
            else:
                logger.error(f"Failed to fetch categories. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Exception during category fetching: {e}")
        return False

    def fetch_products(self, category_id, offset=0):
        limit = 100
        params = {
            'limit': str(limit),
            'offset': str(offset),
            'from': str(offset * limit),
            'filterData[categories]': category_id,
            '_': str(self.get_timestamp()),
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers_api,
                timeout=20
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error {response.status_code} for category {category_id} at offset {offset}")
                return None
        except Exception as e:
            logger.error(f"Exception fetching products for category {category_id}: {e}")
            return None

    def parse_item(self, response_json, category_id):
        if not response_json or 'products' not in response_json:
            return False

        products = response_json['products']
        if not products:
            return False

        found_count = 0
        saved_count = 0

        for p_wrapper in products:
            # Handle both nested 'data' structure and flat structure
            p = p_wrapper.get('data', p_wrapper)
            pdp_url_path = p.get('url')
            
            if not pdp_url_path:
                continue

            # Full URL
            final_url = f"https://mercatoronline.si{pdp_url_path}"
            
            # Check for both codewz (new) and id (legacy)
            product_id = p.get('codewz') or p.get('id')
            
            item = {
                "pdp_url": final_url,
                "category_url": f"https://mercatoronline.si/brskaj#categories={category_id}",
                "product_id": str(product_id) if product_id else None
            }

            found_count += 1
            try:
                response_item = ResponseURLItem(**item)
                response_item.validate()
                self.url_collection.insert_one(item)
                saved_count += 1
            except pymongo.errors.DuplicateKeyError:
                pass
            except Exception as e:
                logger.error(f"  Save error for {final_url}: {e}")

        logger.info(f"Category {category_id}: Found {found_count} products, Saved {saved_count} new products.")
        return True

    def start(self):
        if not self.get_categories():
            logger.error("No categories available to crawl. Exiting.")
            return

        max_retries = 3
        logger.info(f"Starting crawler for {len(self.categories)} categories...")

        for cat_name, cat_id in self.categories.items():
            logger.info(f"Crawling category: {cat_name} ({cat_id})")
            offset = 0
            
            while True:
                success = False
                for attempt in range(max_retries):
                    data = self.fetch_products(cat_id, offset)
                    if data:
                        if self.parse_item(data, cat_id):
                            success = True
                            break
                        else:
                            logger.info(f"No more products for {cat_name} at offset {offset}")
                            success = True 
                            data = None 
                            break
                    else:
                        logger.warning(f"  Attempt {attempt + 1} failed for {cat_name} offset {offset}")
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)

                if not success:
                    logger.error(f"Failed to crawl {cat_name} offset {offset} after {max_retries} attempts")
                    break
                
                if data is None: # parse_item found no products
                    break
                
                offset += 1
                time.sleep(1) # Polite delay

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    crawler_obj = Crawler()
    try:
        crawler_obj.start()
    finally:
        crawler_obj.close()
