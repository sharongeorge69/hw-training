import logging
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_CATEGORY,
    BASE_URL, headers_crawler
)
import pymongo
from items import CategoryItem

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

    def get_brands(self, dept_url: str):
        """Phase 1: Get all brand links from the department page."""
        # XPATH
        BRAND_LINKS_XPATH = "//*[@id='ShopByBrand']/following-sibling::ul[1]//a/@href"

        logger.info(f"Fetching department: {dept_url}")
        try:
            response = requests.get(dept_url, headers=self.headers, impersonate="chrome110", timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed [{response.status_code}]: {dept_url}")
                return []
        except Exception as e:
            logger.error(f"Error fetching {dept_url}: {e}")
            return []

        # EXTRACT
        sel = Selector(text=response.text)
        raw_links = sel.xpath(BRAND_LINKS_XPATH).extract()
        brands = []
        for link in raw_links:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"
            brands.append(link)
        logger.info(f"Found {len(brands)} brand links")
        return brands

    def get_product_types(self, brand_url: str):
        """Phase 2: Get all product type links for a brand."""
        # XPATH
        PRODUCT_TYPE_XPATH = "//h2[contains(normalize-space(), 'Product Types')]/following-sibling::*//a/@href"

        logger.info(f"Fetching brand: {brand_url}")
        try:
            response = requests.get(brand_url, headers=self.headers, impersonate="chrome110", timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed [{response.status_code}]: {brand_url}")
                return []
        except Exception as e:
            logger.error(f"Error fetching {brand_url}: {e}")
            return []

        # EXTRACT
        sel = Selector(text=response.text)
        raw_links = sel.xpath(PRODUCT_TYPE_XPATH).extract()
        product_types = []
        for link in raw_links:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"
            product_types.append(link)
        logger.info(f"Found {len(product_types)} product types for {brand_url}")
        return product_types

    def start(self, dept_url: str, dept_name: str):
        """Phase 3: Drive pagination across all brand + product type model pages."""
        brand_links = self.get_brands(dept_url)

        for brand_url in brand_links:
            brand_name = brand_url.rstrip("/").split("/")[-1].replace("-", " ").title()
            product_type_urls = self.get_product_types(brand_url)

            for pt_url in product_type_urls:
                pt_name = pt_url.rstrip("/").rsplit("/", 2)[-2].replace("-", " ").title()
                models_url = pt_url.rstrip("/") + "/models/"

                page = 1
                while True:
                    url = models_url if page == 1 else f"{models_url}?start={page}"
                    logger.info(f"Fetching: {url}")
                    try:
                        response = requests.get(url, headers=self.headers, impersonate="chrome110", timeout=30)
                    except Exception as e:
                        logger.error(f"Error fetching {url}: {e}")
                        break

                    if response.status_code != 200:
                        logger.error(f"Failed [{response.status_code}]: {url}")
                        break

                    meta = {
                        "department_name": dept_name,
                        "brand_name": f"{brand_name} Parts",
                        "product_type": f"{brand_name} {pt_name} Parts",
                    }

                    is_next = self.parse_item(response, meta)
                    if not is_next:
                        logger.info(f"Pagination completed for {models_url}")
                        break

                    page += 1

    def parse_item(self, response, meta):
        """Extract terminal links from a models page and save to MongoDB.
        Returns True if links were found (continue paginating), False if done."""
        sel = Selector(text=response.text)

        # XPATH
        TERMINAL_LINKS_XPATH = "//ul[contains(@class, 'mini-model-icons')]//a/@href"

        # EXTRACT
        links = sel.xpath(TERMINAL_LINKS_XPATH).extract()
        if not links:
            return False

        for link in links:
            if not link.startswith("http"):
                link = f"{BASE_URL}{link}"

            item = {
                **meta,
                "category_url": link
            }
            try:
                category_item = CategoryItem(**item)
                category_item.validate()
                self.collection.update_one(
                    {"category_url": link},
                    {"$set": item},
                    upsert=True
                )
                logger.info(f"Saved: {link}")
            except pymongo.errors.DuplicateKeyError:
                logger.debug(f"Skipped duplicate: {link}")
            except Exception as e:
                logger.error(f"Failed to save {link}: {e}")

        return True

    def close(self):
        """Close MongoDB connection."""
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
