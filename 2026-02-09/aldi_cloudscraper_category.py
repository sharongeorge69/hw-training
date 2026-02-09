import cloudscraper
from parsel import Selector
import logging
from pymongo import MongoClient
import aldi_settings as settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Category:

    def __init__(self):
        #Initialize MongoDB
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY_CLOUDSCRAPER]
        
        #unique index on URL
        self.collection.create_index("url", unique=True)
        
        # Initialize CloudScraper
        self.scraper = cloudscraper.create_scraper()
        self.sitemap_url = settings.SITEMAP_URL

    def start(self):
        logger.info("Requesting Sitemap: %s", self.sitemap_url)

        try:
            # Fetch Sitemap Page
            try:
                sitemap_response = self.scraper.get(self.sitemap_url)
                sitemap_response.raise_for_status()
            except Exception as e:
                logger.error("Error fetching sitemap: %s", e)
                return

            # Extract Category URLs 
            selector = Selector(text=sitemap_response.text)
            links = selector.xpath("//a")
            logger.info("Total links found: %s", len(links))

            category_urls = []
            seen_urls = set()
            
            for link in links:
                href = link.xpath("@href").get()
                text = link.xpath("normalize-space()").get()

                # Resolve relative URLs
                full_url = ""
                if href and not href.startswith("http"):
                    full_url = "https://www.aldi.us" + href
                
                # Apply filtering logic
                if full_url and "aldi.us" in full_url and "/products/" in full_url and "/product/" not in full_url:
                    if full_url not in seen_urls:
                        category_urls.append((text, full_url))
                        seen_urls.add(full_url)
                        
                        # Save to MongoDB
                        self.save_to_mongo(text, full_url)

            logger.info("Found %s Unique Category URLs", len(category_urls))

        except Exception as e:
            logger.error("Error during scraping: %s", e)
        finally:
            self.close()

    #save to mongo
    def save_to_mongo(self, text, url):
        item = {
            "category_name": text,
            "url": url
        }
        try:
            # Upsert using URL as unique key
            self.collection.update_one(
                {"url": url},
                {"$set": item},
                upsert=True
            )
            logger.info("Saved Category: %s -> %s", text, url)
        except Exception as e:
            logger.error("Error saving to MongoDB: %s", e)

    def close(self):
        #close mongo connection
        if self.client:
            self.client.close()

if __name__ == "__main__":
    crawler = Category()
    crawler.start()