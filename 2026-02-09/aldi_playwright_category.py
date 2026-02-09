from playwright.sync_api import sync_playwright
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
        # Initialize MongoDB
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY_PLAYWRIGHT]
        
        # Ensure unique index on URL to prevent duplicates at DB level
        self.collection.create_index("url", unique=True)

    def start(self):
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            try:
                page.goto(settings.BASE_URL)
                logger.info("Navigated to Homepage")

                # Click Cookie Banner if it appears
                try:
                    page.click("//button[contains(., 'Got it')]", timeout=10000)
                    logger.info("Clicked Cookie Banner")
                except Exception:
                    logger.warning("Cookie banner did not appear or was not clickable")

                # Scroll to bottom
                page.evaluate("window.scrollTo(0, document.body.scrollHeight);")

                # Click Sitemap
                try:
                    page.click("text=Sitemap")
                    logger.info("Clicked Sitemap. Current URL: %s", page.url)
                except Exception as e:
                    logger.error("Could not click Sitemap: %s", e)
                    return

                page.wait_for_selector("body")

                # Extract all links
                links_data = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a')).map(a => ({
                        text: a.innerText,
                        href: a.href
                    }));
                }""")
                
                logger.info("Total links found: %s", len(links_data))

                category_urls = []
                seen_urls = set()
                
                for item in links_data:
                    url = item.get('href')
                    text = item.get('text', '').strip()
                    
                    #filtering the urls
                    if url and "aldi.us" in url and "/products/" in url and "/product/" not in url:
                        if url not in seen_urls:
                            category_urls.append((text, url))
                            seen_urls.add(url)
                            
                            # Save to MongoDB
                            self.save_to_mongo(text, url)

                logger.info("Found %s Unique Category URLs", len(category_urls))

            except Exception as e:
                logger.error("Error during scraping: %s", e)
            finally:
                browser.close()
                self.close()
    #save to mongo db
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
        if self.client:
            self.client.close()

if __name__ == "__main__":
    crawler = Category()
    crawler.start()
