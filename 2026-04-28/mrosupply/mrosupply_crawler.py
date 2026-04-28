import logging
import time
import re
import requests
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
        logger.info(f"Fetching main sitemap: {self.main_sitemap}")
        for attempt in range(max_retries):
            try:
                response = requests.get(self.main_sitemap, headers=self.headers, timeout=60)
                if response.status_code == 200:
                    selector = Selector(text=response.text, type='xml')
                    
                    # Try to find sub-sitemaps (sitemapindex)
                    sitemaps = selector.xpath('//*[local-name()="loc"]/text()').getall()
                    
                    # Filter for product sitemaps
                    product_sitemaps = [s for s in sitemaps if "sitemap-product" in s]
                    
                    if not product_sitemaps and sitemaps:
                        # If no "sitemap-product" found but locs exist, maybe the main sitemap IS a product sitemap or we should just check all locs
                        # But standard is to have product sitemaps.
                        # For MROSupply, the sample showed sitemap-product-1.xml
                        logger.warning("No sitemaps with 'sitemap-product' found. Checking all locs.")
                        product_sitemaps = sitemaps

                    if not product_sitemaps:
                        # Fallback to known pattern if still empty
                        logger.warning("Main sitemap did not return sub-sitemaps. Trying known pattern.")
                        return ["https://www.mrosupply.com/sitemap-product-1.xml"]

                    return product_sitemaps
                else:
                    logger.warning(f"  Attempt {attempt + 1} failed for main sitemap. Status: {response.status_code}")
            except Exception as e:
                logger.warning(f"  Attempt {attempt + 1} failed for main sitemap with error: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        logger.error(f"Failed to fetch main sitemap after {max_retries} attempts.")
        # Fallback to sample URL
        return ["https://www.mrosupply.com/sitemap-product-1.xml"]

    def parse_item(self, sitemap_url):
        logger.info(f"Crawling sitemap: {sitemap_url}")
        try:
            response = requests.get(sitemap_url, headers=self.headers, timeout=60)
            if response.status_code != 200:
                logger.error(f"Failed to fetch sitemap: {sitemap_url}. Status: {response.status_code}")
                return False

            selector = Selector(text=response.text, type='xml')
            
            urls = selector.xpath('//*[local-name()="loc"]/text()').getall()
            # Filter only product URLs
            product_urls = [url for url in urls if "/product/" in url]

            if not product_urls:
                logger.warning(f"No products found on {sitemap_url}")
                # Check if it contains sub-sitemaps (just in case)
                sub_sitemaps = [u for u in urls if ".xml" in u and u != sitemap_url]
                if sub_sitemaps:
                    logger.info(f"Detected sub-sitemaps in what was expected to be a leaf sitemap: {len(sub_sitemaps)}")
                    for sub in sub_sitemaps:
                        self.parse_item(sub)
                    return True
                return True 

            found_count = 0
            saved_count = 0
            
            for pdp_url in product_urls:
                item = {
                    "pdp_url": pdp_url,
                    "category_url": sitemap_url,
                }
                
                # Extract product id if possible from URL (e.g. /product/12345-name)
                match = re.search(r"/product/(\d+)", pdp_url)
                if match:
                    item["product_id"] = match.group(1)

                found_count += 1
                try:
                    # Validate using the Item class (if needed for strictness)
                    # response_item = ResponseURLItem(**item)
                    # response_item.validate()
                    
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
        logger.info("Starting MROSupply crawler...")
        
        product_sitemaps = self.get_product_sitemaps(max_retries=max_retries)
        if not product_sitemaps:
            logger.error("No product sitemaps found. Exiting.")
            return

        logger.info(f"Total product sitemaps found to process: {len(product_sitemaps)}")

        for sitemap_url in product_sitemaps:
            success = False
            for attempt in range(max_retries):
                if self.parse_item(sitemap_url):
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
