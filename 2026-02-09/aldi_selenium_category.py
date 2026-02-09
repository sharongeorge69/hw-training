import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

import aldi_settings as settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Category:
    def __init__(self):
        # Initialize Selenium Driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 10)
        
        # Initialize MongoDB
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY]
        #unique index on url
        self.collection.create_index("url", unique=True)

    def start(self):
        try:
            self.driver.get(settings.BASE_URL)
            logger.info("Navigated to Homepage")
            
            # Cookie Banner
            try:
                accept_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Got it')]"))
                )
                accept_btn.click()
                logger.info("Clicked Cookie Banner")
            except Exception as e:
                logger.warning("Cookie banner not found or error clicking: %s", e)

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Sitemap Link
            sitemap = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sitemap")))
            sitemap.click()
            logger.info("Clicked Sitemap. Current URL: %s", self.driver.current_url)

            # Wait for body to ensure page load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Extract all links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            logger.info("Total links found: %s", len(links))

            category_urls = []
            seen_urls = set()
            
            for link in links:
                url = link.get_attribute("href")
                if url and "aldi.us" in url and "/products/" in url and "/product/" not in url:
                    text = link.get_attribute("textContent").strip()
                    if url not in seen_urls:
                        category_urls.append((text, url))
                        seen_urls.add(url)
                        
                        # Save to MongoDB
                        self.save_to_mongo(text, url)

            logger.info("Found %s Unique Category URLs", len(category_urls))
            
        except Exception as e:
            logger.error("Error during scraping: %s", e)
        finally:
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
        if self.driver:
            self.driver.quit()
        if self.client:
            self.client.close()


if __name__ == "__main__":
    crawler = Category()
    crawler.start()
