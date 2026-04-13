import logging
import time
import requests
from parsel import Selector
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

        self.categories = {}

    def get_categories(self):
        """
        Fetches categories and their IDs from the website.
        """
        logger.info("Fetching categories from site...")
        try:
            response = requests.get('https://mercatoronline.si/brskaj', headers=self.headers_html, timeout=20)
            if response.status_code == 200:
                selector = Selector(text=response.text)
                
                # XPATH
                CATEGORY_NAMES_XPATH = '//li[contains(@class, "lib-category-menu-top")]/a/@data-analytics-label'
                CATEGORY_IDS_XPATH = '//li[contains(@class, "lib-category-menu-top")]/@data-category-id'
                
                # EXTRACT
                category_names = selector.xpath(CATEGORY_NAMES_XPATH).extract()
                category_ids = selector.xpath(CATEGORY_IDS_XPATH).extract()
                
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

    def parse_item(self, response_json, category_id):
        if not response_json or 'products' not in response_json:
            return False

        products = response_json['products']
        if not products:
            return False

        found_count = 0
        saved_count = 0
        category_url = f"https://mercatoronline.si/brskaj#categories={category_id}"

        for product_wrapper in products:
            found_count += 1
            nested_data = product_wrapper.get('data', {})
            
            # Determine URL
            pdp_url_path = product_wrapper.get('url') or nested_data.get('url')
            if not pdp_url_path:
                continue

            # VARIABLES
            final_url = f"https://mercatoronline.si{pdp_url_path}" if pdp_url_path.startswith('/') else pdp_url_path
            raw_id = nested_data.get('codewz') or product_wrapper.get('itemId') or nested_data.get('id')
            product_id = str(raw_id) if raw_id else None

            # ITEM
            item = product_wrapper.copy()
            item["pdp_url"] = final_url
            item["category_url"] = category_url
            item["product_id"] = product_id

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

        for category_name, category_id in self.categories.items():
            logger.info(f"Crawling category: {category_name} ({category_id})")
            offset = 0
            
            while True:
                success = False
                json_data = None
                
                # Inline fetching logic
                params = {
                    'limit': '100',
                    'offset': str(offset),
                    'from': str(offset * 100),
                    'filterData[categories]': category_id,
                }
                
                for attempt in range(max_retries):
                    try:
                        response = requests.get(
                            self.base_url,
                            params=params,
                            headers=self.headers_api,
                            timeout=20
                        )
                        if response.status_code == 200:
                            json_data = response.json()
                            if self.parse_item(json_data, category_id):
                                success = True
                                break
                            else:
                                logger.info(f"No more products for {category_name} at offset {offset}")
                                success = True 
                                json_data = None 
                                break
                        else:
                            logger.warning(f"  Attempt {attempt + 1} failed for {category_name} offset {offset} with code {response.status_code}")
                    except Exception as e:
                        logger.warning(f"  Attempt {attempt + 1} failed for {category_name} offset {offset} with error: {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)

                if not success:
                    logger.error(f"Failed to crawl {category_name} offset {offset} after {max_retries} attempts")
                    break
                
                if json_data is None: 
                    break
                
                offset += 1

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
