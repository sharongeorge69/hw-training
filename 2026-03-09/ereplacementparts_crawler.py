import logging
import pymongo
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_CATEGORY,
    MONGO_COLLECTION_RESPONSE,
    BASE_URL, headers_crawler
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self):
        self.headers = headers_crawler

        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.category_collection = self.db[MONGO_COLLECTION_CATEGORY]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.url_collection.create_index("pdp_url", unique=True)
        logger.info("Connected to MongoDB")

    def start(self):
        """Read category URLs from MongoDB and extract PDP links."""
        total = self.category_collection.count_documents({})
        logger.info(f"Total category URLs to process: {total}")

        for idx, doc in enumerate(self.category_collection.find(), 1):
            category_url = doc.get("category_url")
            if not category_url:
                continue

            logger.info(f"Processing {idx}/{total}: {category_url}")
            try:
                response = requests.get(category_url, headers=self.headers, impersonate="chrome110", timeout=30)
                if response.status_code == 200:
                    self.parse_item(response, doc)
                else:
                    logger.error(f"Failed [{response.status_code}]: {category_url}")
            except Exception as e:
                logger.error(f"Error fetching {category_url}: {e}")

    def parse_item(self, response, meta):
        """Extract PDP links from a category page and save to MongoDB."""
        sel = Selector(text=response.text)

        # XPATH
        PDP_LINKS_XPATH = '//ul[@data-list-type="sections"]//a/@href'

        # EXTRACT
        raw_links = sel.xpath(PDP_LINKS_XPATH).extract()
        unique_links = list(dict.fromkeys(raw_links))  

        for link in unique_links:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"

            # Strip query params before saving
            clean_url = link.split("?")[0]

            item = {
                "pdp_url": clean_url,
                "department_name": meta.get("department_name", ""),
                "brand_name": meta.get("brand_name", ""),
                "product_type": meta.get("product_type", ""),
                "category_url": meta.get("category_url", "")
            }

            try:
                self.url_collection.insert_one(item)
                logger.info(f"Saved: {clean_url}")
            except pymongo.errors.DuplicateKeyError:
                pass 
            except Exception as e:
                logger.error(f"Save error for {clean_url}: {e}")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass


if __name__ == "__main__":
    crawler_obj = Crawler()
    crawler_obj.start()
    crawler_obj.close()
