import style_union_settings as settings
import requests
from parsel import Selector
import logging
import pymongo
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StyleUnionCategory:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.headers = settings.HEADERS
        
        # MongoDB connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.DB_NAME
        self.collection_name = settings.COLLECTION_CATEGORY
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_category_urls(self):
        try:
            logger.info(f"Fetching category URLs from {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()

            sel = Selector(text=response.text)
            
            # Use the xpath provided by the user
            category_links = sel.xpath("//div[contains(@class,'list-menu-dropdown')]//div[contains(@class,'menu__dropdown-grandchild-container')]//li/a/@href").getall()
            
            full_urls = []
            for link in category_links:
                if link:
                    # Join the prefix of the link with "https://styleunion.in/"
                    # Handling relative paths properly
                    if link.startswith("http"):
                         full_urls.append(link)
                    else:
                        full_urls.append(f"{self.base_url.rstrip('/')}/{link.lstrip('/')}")
            
            logger.info(f"Found {len(full_urls)} category URLs")
            return full_urls

        except requests.RequestException as e:
            logger.error(f"Error fetching category URLs: {e}")
            return []

    def save_to_db(self, urls):
        if not urls:
            logger.warning("No URLs to save")
            return

        added_count = 0
        matched_count = 0
        for url in urls:
            try:
                # Upsert logic to handle duplicates and preserve status if exists
                result = self.collection.update_one(
                    {"url": url},
                    {
                        "$setOnInsert": {
                            "url": url,
                            "created_at": datetime.now()
                        }
                    },
                    upsert=True
                )
                
                if result.upserted_id:
                    added_count += 1
                else:
                    matched_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving URL {url}: {e}")
        
        logger.info(f"Database update complete. Added: {added_count}, Updated/Existing: {matched_count}")

if __name__ == "__main__":
    scraper = StyleUnionCategory()
    urls = scraper.get_category_urls()
    scraper.save_to_db(urls)
