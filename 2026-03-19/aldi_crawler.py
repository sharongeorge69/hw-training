import logging
import time
import requests
from parsel import Selector
import re
from pymongo import MongoClient
import pymongo
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, headers
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
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        
        # Create unique index to avoid duplicates
        self.url_collection.create_index("pdp_url", unique=True)
        logger.info("Connected to MongoDB") 

    def parse_item(self, response_text, url):
        selector = Selector(text=response_text)
        snippet_urls = selector.xpath("//div[@data-tile-url]/@data-tile-url").getall()

        base = "https://www.aldi.be"
        
        # Extract the category path for the hash, e.g., /nl/producten/assortiment/...
        category_hash = ""
        category_hash = url.split("aldi.be")[1].replace(".html", "")

        found_count = 0
        saved_count = 0
        
        for snippet_url in snippet_urls:
            match = re.search(r"snippet-(.*)\.shoppinglisttile", snippet_url)
            if match:
                product_id = match.group(1)
                
                # The product text doesn't matter for the backend, just the ID
                final_url = f"{base}/nl/p/artikel-{product_id}.article.html#{category_hash}"
                item = {}
                item["pdp_url"] = final_url
                item["category_url"] = url
                item["product_id"] = product_id
                
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
                    
        logger.info(f"Found {found_count} products, Saved {saved_count} new products.")
        return True

    def start(self):
        target_urls = [
            "https://www.aldi.be/nl/producten/assortiment/alcoholvrije-dranken/energy-drinks-sportdrank.html",
            "https://www.aldi.be/nl/producten/assortiment/alcoholvrije-dranken/limonades.html",
        ]
        
        max_retries = 3
        logger.info(f"Starting crawler for {len(target_urls)} categories...")
        
        for url in target_urls:
            logger.info(f"Crawling category: {url}")
            success = False
            for attempt in range(max_retries):
                try:
                    # Fast timeout
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        self.parse_item(response.text, url)
                        success = True
                        break
                    else:
                        logger.warning(f"  Attempt {attempt + 1} failed for {url} with status code {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"  Attempt {attempt + 1} failed for {url} with error: {e}")
                
                # Exponential backoff on retry (skipped on last attempt)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            if not success:
                logger.error(f"Failed to crawl {url} after {max_retries} attempts")

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