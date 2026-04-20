import logging
import time
import re
from pymongo import MongoClient
import pymongo
from parsel import Selector
from camoufox.sync_api import Camoufox

from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, SITEMAP_URL, headers
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
        self.main_sitemap = SITEMAP_URL
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        
        self.url_collection.create_index("pdp_url", unique=True)
        logger.info("Connected to MongoDB")

    def get_product_sitemaps(self, page, max_retries=3):
        logger.info(f"Fetching main sitemap: {self.main_sitemap}")
        for attempt in range(max_retries):
            try:
                response = page.goto(self.main_sitemap, wait_until="load", timeout=60000)
                if response and response.status == 200:
                    content = response.body().decode('utf-8')
                    selector = Selector(text=content, type='xml')
                    
                    product_sitemaps = selector.xpath('//*[local-name()="loc"][contains(text(), "sitemap_products")]/text()').getall()
                    return product_sitemaps
                else:
                    logger.warning(f"  Attempt {attempt + 1} failed for main sitemap. Status: {response.status if response else 'No Response'}")
            except Exception as e:
                logger.warning(f"  Attempt {attempt + 1} failed for main sitemap with error: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        logger.error(f"Failed to fetch main sitemap after {max_retries} attempts.")
        return []

    def parse_item(self, page, sitemap_url):
        logger.info(f"Crawling sitemap: {sitemap_url}")
        try:
            response = page.goto(sitemap_url, wait_until="load", timeout=60000)
            if not response or response.status != 200:
                logger.error(f"Failed to fetch sitemap: {sitemap_url}. Status: {response.status if response else 'No Response'}")
                return False

            content = response.body().decode('utf-8')
            selector = Selector(text=content, type='xml')
            
            urls = selector.xpath('//*[local-name()="loc"]/text()').getall()
            product_urls = [url for url in urls if "/products/" in url]

            if not product_urls:
                logger.warning(f"No products found on {sitemap_url}")
                return True # Not a failure, just empty

            found_count = 0
            saved_count = 0
            
            for pdp_url in product_urls:
                item = {
                    "pdp_url": pdp_url,
                    "category_url": sitemap_url,
                }
                
                # Extract product id if possible from URL
                match = re.search(r"num-(.*)$", pdp_url)
                if match:
                    item["product_id"] = match.group(1)

                found_count += 1
                try:
                    # Validate using the Item class
                    response_item = ResponseURLItem(**item)
                    response_item.validate()
                    
                    # Save using pymongo
                    self.url_collection.insert_one(item)
                    saved_count += 1
                except pymongo.errors.DuplicateKeyError:
                    pass
                except Exception as e:
                    logger.error(f"  Save error for {pdp_url}: {e}")
            
            logger.info(f"Found {found_count} products, Saved {saved_count} new products from {sitemap_url}")
            return True

        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
            return False

    def start(self):
        max_retries = 3
        logger.info("Starting crawler...")
        with Camoufox(headless=True) as browser:
            page = browser.new_page()
            
            product_sitemaps = self.get_product_sitemaps(page, max_retries=max_retries)
            if not product_sitemaps:
                logger.error("No product sitemaps found. Exiting.")
                return

            logger.info(f"Total product sitemaps found: {len(product_sitemaps)}")

            for sitemap_url in product_sitemaps:
                success = False
                for attempt in range(max_retries):
                    if self.parse_item(page, sitemap_url):
                        success = True
                        break
                    else:
                        logger.warning(f"  Attempt {attempt + 1} failed for sitemap: {sitemap_url}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                
                if not success:
                    logger.error(f"Failed to process sitemap after {max_retries} attempts: {sitemap_url}")
                
                time.sleep(1)

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

if __name__ == "__main__":
    crawler_obj = Crawler()
    try:
        crawler_obj.start()
    except Exception as e:
        logger.critical(f"Crawler crashed: {e}")
    finally:
        crawler_obj.close()