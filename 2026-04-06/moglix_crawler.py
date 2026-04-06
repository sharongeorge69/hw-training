import logging
import time
import requests
import pymongo
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE,
    headers, CATEGORY_LIST
)
from items import ResponseURLItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.headers = headers
        self.mongo_uri = MONGO_URI
        self.mongo_db_name = MONGO_DB
        self.collection_name = MONGO_COLLECTION_RESPONSE
        
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db_name]
            self.url_collection = self.db[self.collection_name]
            
            self.url_collection.create_index("pdp_url", unique=True)
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def parse_item(self, response_text, category_name, category_url):
        if not response_text:
            logger.error(f"Received empty response content for {category_name}")
            return 0

        try:
            selector = Selector(text=response_text)
            product_links = selector.xpath('//a[contains(@href, "/mp/")]/@href').getall()
            
            if not product_links:
                logger.warning(f"No products found on page for category '{category_name}'")
                return 0

            found_on_page = 0
            saved_to_db = 0

            unique_links = set(product_links)
            
            for link in unique_links:      
                item_data = {
                    "pdp_url": link,
                    "category_name": category_name,
                    "category_url": category_url
                }
                
                found_on_page += 1
                try:
                    response_item = ResponseURLItem(**item_data)
                    response_item.validate()
                    
                    self.url_collection.insert_one(item_data)
                    saved_to_db += 1
                except pymongo.errors.DuplicateKeyError:
                    pass
                except Exception as e:
                    logger.error(f"Error saving product URL {link}: {e}")
            
            logger.info(f"[{category_name}] Products found: {found_on_page}, New products saved: {saved_to_db}")
            return found_on_page

        except Exception as e:
            logger.error(f"Error during parsing of category '{category_name}': {e}")
            return 0

    def start(self):
        categories = CATEGORY_LIST
        max_retries = 3
        
        logger.info(f"Starting Moglix crawl for {len(categories)} categories...")
        
        for category_name, base_url in categories.items():
            logger.info(f"Crawling Category: {category_name}")
            page_index = 1
            
            while True:
                paginated_url = f"{base_url}?page={page_index}"
                logger.info(f"  Requesting Page {page_index}: {paginated_url}")
                
                operation_success = False
                products_count = 0
                
                for attempt in range(max_retries):
                    try:
                        response = requests.get(paginated_url, headers=self.headers, timeout=15)
                        
                        if response.status_code == 200:
                            products_count = self.parse_item(response.text, category_name, base_url)
                            operation_success = True
                            break
                        else:
                            logger.warning(f"  Attempt {attempt + 1}: Failure for {paginated_url} (HTTP {response.status_code})")
                    
                    except Exception as e:
                        logger.warning(f"  Attempt {attempt + 1}: Error for {paginated_url}: {e}")
                    
                    # Exponential backoff
                    if attempt < max_retries - 1:
                        backoff_seconds = 2 ** attempt
                        logger.info(f"  Waiting {backoff_seconds}s before retrying...")
                        time.sleep(backoff_seconds)
                
                if not operation_success:
                    logger.error(f"Exhausted retries for {paginated_url}. Skipping category mapping.")
                    break
                
                if products_count == 0:
                    logger.info(f"No more products found. Finished crawling {category_name}.")
                    break
                
                page_index += 1

    def close(self):
        try:
            self.client.close()
            logger.info("connection closed")
        except Exception as e:
            logger.error(f"Error while closing MongoDB connection: {e}")

if __name__ == "__main__":
    moglix_crawler = Crawler()
    try:
        moglix_crawler.start()
    finally:
        moglix_crawler.close()
