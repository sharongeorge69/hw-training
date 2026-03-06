import logging
import random
import time
from typing import List
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_CATEGORY,
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
        self.collection = self.db[MONGO_COLLECTION_CATEGORY]
        self.collection.create_index("category_url", unique=True)
        logger.info("Connected to MongoDB")

    def fetch(self, url: str) -> Selector:
        """Fetch a URL and return a Selector."""
        time.sleep(random.uniform(1.5, 3.0))
        logger.info(f"Fetching: {url}")
        try:
            response = requests.get(url, headers=self.headers, impersonate="chrome110", timeout=30)
            if response.status_code == 200:
                return Selector(text=response.text)
            logger.error(f"Failed [{response.status_code}]: {url}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def get_brands(self, dept_url: str) -> List[str]:
        """Phase 1: Get all brand links from the department page."""
        sel = self.fetch(dept_url)
        if not sel:
            return []
        brand_links = sel.xpath("//*[@id='ShopByBrand']/following-sibling::ul[1]//a/@href").getall()
        brands = []
        for link in brand_links:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"
            brands.append(link)
        logger.info(f"Found {len(brands)} brand links")
        return brands

    def get_product_types(self, brand_url: str) -> List[str]:
        """Phase 2: Get all product type links for a brand."""
        sel = self.fetch(brand_url)
        if not sel:
            return []
        # Extract using dynamic heading: e.g. "All Bosch Product Types"
        part_urls = sel.xpath("//h2[contains(normalize-space(), 'Product Types')]/following-sibling::*//a/@href").getall()
        product_types = []
        for link in part_urls:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"
            product_types.append(link)
        logger.info(f"Found {len(product_types)} product types for {brand_url}")
        return product_types

    def get_terminal_links(self, models_url: str) -> List[str]:
        """Phase 3: Paginate through the /models/ page and collect all terminal links."""
        terminal_links = []
        page = 1

        while True:
            url = models_url if page == 1 else f"{models_url}?start={page}"
            sel = self.fetch(url)
            if not sel:
                break

            links = sel.xpath("//ul[contains(@class, 'mini-model-icons')]//a/@href").getall()
            if not links:
                break  # No more results, stop paging

            for link in links:
                if not link.startswith("http"):
                    link = f"{BASE_URL}{link}"
                terminal_links.append(link)

            page += 1

        logger.info(f"Found {len(terminal_links)} terminal links under {models_url}")
        return terminal_links

    def save(self, data: dict):
        """Save a terminal page record to MongoDB."""
        try:
            self.collection.update_one(
                {"category_url": data["category_url"]},
                {"$set": data},
                upsert=True
            )
            logger.info(f"Saved: {data['category_url']}")
        except Exception as e:
            logger.error(f"Failed to save: {e}")

    def start(self, dept_url: str, dept_name: str):
        """Main extraction flow for a single department."""
        brand_links = self.get_brands(dept_url)

        for brand_url in brand_links:
            # e.g. https://www.ereplacementparts.com/parts/bosch/
            brand_name = brand_url.rstrip("/").split("/")[-1].replace("-", " ").title()

            product_type_urls = self.get_product_types(brand_url)

            for pt_url in product_type_urls:
                # e.g. https://www.ereplacementparts.com/parts/appliance/dishwasher/bosch/
                pt_name = pt_url.rstrip("/").rsplit("/", 2)[-2].replace("-", " ").title()

                # Append /models/ to get to the terminal listing page
                models_url = pt_url.rstrip("/") + "/models/"

                terminal_links = self.get_terminal_links(models_url)

                for terminal_url in terminal_links:
                    data = {
                        "department_name": dept_name,
                        "brand_name": f"{brand_name} Parts",
                        "product_type": f"{brand_name} {pt_name} Parts",
                        "category_url": terminal_url
                    }
                    self.save(data)

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass


if __name__ == "__main__":
    crawler_obj = Crawler()
    crawler_obj.start(
        dept_url="https://www.ereplacementparts.com/parts/appliance/",
        dept_name="Appliance Parts"
    )
    crawler_obj.close()
