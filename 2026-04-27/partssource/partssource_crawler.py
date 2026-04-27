import logging
import time
import re
import gzip
import io
import requests
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
import pymongo
from parsel import Selector

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

    def get_product_sitemaps(self, max_retries=3):
        logger.info(f"Fetching sitemap index: {self.main_sitemap}")
        for attempt in range(max_retries):
            try:
                response = requests.get(self.main_sitemap, headers=self.headers, timeout=60)
                if response.status_code == 200:
                    selector = Selector(text=response.text, type='xml')
                    sub_sitemaps = selector.xpath('//*[local-name()="loc"]/text()').getall()
                    return sub_sitemaps
                else:
                    logger.warning(f"  Attempt {attempt + 1} failed for main sitemap. Status: {response.status_code}")
            except Exception as e:
                logger.warning(f"  Attempt {attempt + 1} failed for main sitemap with error: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        logger.error(f"Failed to fetch main sitemap after {max_retries} attempts.")
        return []

    def parse_item(self, sitemap_url):
        # This function will be called by ThreadPoolExecutor
        logger.info(f"Processing sitemap: {sitemap_url}")
        try:
            response = requests.get(sitemap_url, headers=self.headers, timeout=60)
            if response.status_code != 200:
                logger.error(f"Failed to fetch sitemap: {sitemap_url}. Status: {response.status_code}")
                return 0, 0

            content = response.content
            # Handle gzip if necessary
            if sitemap_url.endswith('.gz'):
                try:
                    with gzip.GzipFile(fileobj=io.BytesIO(content)) as f:
                        content = f.read().decode('utf-8')
                except Exception as e:
                    logger.error(f"Error decompressing {sitemap_url}: {e}")
                    return 0, 0
            else:
                content = content.decode('utf-8')

            selector = Selector(text=content, type='xml')
            urls = selector.xpath('//*[local-name()="loc"]/text()').getall()
            
            # Filter for products - strictly URLs that start with /parts/ after the domain
            product_urls = [u for u in urls if "https://www.partssource.com/parts/" in u]

            if not product_urls:
                return 0, 0

            found_count = 0
            saved_count = 0
            
            for pdp_url in product_urls:
                item = {
                    "pdp_url": pdp_url,
                    "category_url": sitemap_url,
                }                

                found_count += 1
                try:
                    self.url_collection.insert_one(item)
                    saved_count += 1
                except pymongo.errors.DuplicateKeyError:
                    pass
                except Exception as e:
                    # Ignore occasional errors during high concurrency unless critical
                    pass
            
            return found_count, saved_count

        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
            return 0, 0

    def start(self):
        logger.info("Starting PartsSource crawler...")
        
        sub_sitemaps = self.get_product_sitemaps()
        if not sub_sitemaps:
            logger.error("No sub-sitemaps found. Exiting.")
            return

        total_sitemaps = len(sub_sitemaps)
        logger.info(f"Total sub-sitemaps to process: {total_sitemaps}")

        total_found = 0
        total_saved = 0
        
        # Use ThreadPoolExecutor for high-concurrency
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.parse_item, sub_sitemaps))
            
            for found, saved in results:
                total_found += found
                total_saved += saved

        logger.info(f"Finished crawling PartsSource. Total Found: {total_found}, Total Saved: {total_saved}")

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
