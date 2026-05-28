import logging
import re
import time
import requests
from datetime import datetime
from pymongo import MongoClient
import pymongo
from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE,
    MONGO_COLLECTION_URL_FAILED,
    API_URL, PRODUCT_BASE_URL,
    MAX_RETRIES, headers, category_configs,
)
from items import ResponseURLItem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


_UNITS = r'(kg|g|gm|mg|ml|l)'


def extract_grammage(product_name):
    if not product_name:
        return ""
    cleaned = re.sub(
        r'\((?:Pack of \d+|Carton|Tub|Bottle|Tetra Pack|Tetra Pak|Super Saver Pack)\)',
        '', product_name, flags=re.IGNORECASE
    )
    m = re.search(r'(\d+\+\d+)\s*' + _UNITS + r'\b', cleaned, re.IGNORECASE)
    if m:
        return f"{m.group(1)} {m.group(2).lower()}"
    m = re.search(r'(\d+)\s*' + _UNITS + r'\s*x\s*\d+', cleaned, re.IGNORECASE)
    if m:
        return f"{m.group(1)} {m.group(2).lower()}"
    m = re.search(r'\d+x(\d+)\s*' + _UNITS + r'\b', cleaned, re.IGNORECASE)
    if m:
        return f"{m.group(1)} {m.group(2).lower()}"
    m = re.search(r'(\d+(?:\.\d+)?)\s*' + _UNITS + r'\b', cleaned, re.IGNORECASE)
    if m:
        return f"{m.group(1)} {m.group(2).lower()}"
    return ""


class Crawler:
    def __init__(self):
        self.headers = headers
        self.session = requests.Session()

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]

        self.url_collection.create_index("product_url", unique=True)
        logger.info("Connected to MongoDB")


    def parse_item(self, product, category_url):
        uid = product.get("uid")
        product_id = str(uid)
        if not product_id:
            return None

        slug = product.get("slug", "")
        product_url = f"{PRODUCT_BASE_URL}{slug}" if slug else ""

        name = product.get("name", "")
        brand = product.get("brand", {})
        brand_name = brand.get("name", "") if isinstance(brand, dict) else ""

        hierarchy = product.get("hierarchy", {}) or {}
        l1_category = hierarchy.get("l1_category", {}).get("name", "")
        l2_category = hierarchy.get("l2_category", {}).get("name", "")
        l3_category = hierarchy.get("l3_category", {}).get("name", "")
        taxonomy_parts = [l1_category,l2_category,l3_category]
        taxonomy = " > ".join([part for part in taxonomy_parts if part])

        cat_name = l3_category

        price = product.get("price", {}) or {}
        effective = price.get("effective", {}) or {}
        marked = price.get("marked", {}) or {}
        selling_price = str(effective.get("min", ""))
        mrp = str(marked.get("min", ""))

        medias = product.get("medias", []) or []
        main_image = ""
        all_images = []
        if medias:
            main_image = medias[0].get("url", "")
            all_images = [m.get("url", "") for m in medias if m.get("url")]

        country_of_origin = product.get("country_of_origin", "")
        seller_id = product.get("seller_id", "")
        sku_code = product.get("sku_code", "")
        extraction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        item = {}
        item['product_url'] = product_url
        item['product_id'] = product_id
        item['category_url'] = category_url
        item['category_name'] = cat_name
        item['product_name'] = name
        item['brand'] = brand_name
        item['grammage'] = extract_grammage(name)
        item['sku_code'] = sku_code
        item['taxonomy'] = taxonomy
        item['selling_price'] = selling_price
        item['mrp'] = mrp
        item['main_image_url'] = main_image
        item['image_urls'] = all_images
        item['country_of_origin'] = country_of_origin or ""
        item['extraction_date'] = extraction_date
        item['seller_id'] = str(seller_id) if seller_id else ""
        return item

    def fetch_page(self, f_param, page_no, page_size=40):
        params = {
            "f": f_param,
            "page_id": "*",
            "page_no": str(page_no),
            "page_size": str(page_size),
            "page_type": "number",
            "sort_on": "popular",
        }
        response = self.session.get(API_URL, params=params, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def parse_products(self, data, category_url, category_name):
        items = data.get("items", [])
        if not items:
            logger.warning(f"No products found in response for {category_url}")
            return False

        found_count = 0
        saved_count = 0

        for product in items:
            parsed = self.parse_item(product, category_url)
            if not parsed:
                continue

            found_count += 1
            try:
                response_item = ResponseURLItem(**parsed)
                response_item.validate()
                self.url_collection.insert_one(parsed)
                saved_count += 1
            except pymongo.errors.DuplicateKeyError:
                pass
            except Exception as e:
                logger.error(f"Save error for {parsed.get('product_url', '')}: {e}")

        logger.info(f"Found {found_count} products, Saved {saved_count} new.")
        return True

    def crawl_category(self, config):
        url = config["url"]
        f_param = config["f"]
        name = config.get("name", "")
        logger.info(f"Crawling category: {name or url}")

        page_no = 1
        total_saved = 0

        while True:
            logger.info(f"  Fetching page {page_no}...")
            success = False
            for attempt in range(MAX_RETRIES):
                try:
                    data = self.fetch_page(f_param, page_no)
                    page_info = data.get("page", {}) or {}
                    has_next = page_info.get("has_next", False)

                    if self.parse_products(data, url, name):
                        success = True
                        total_saved += 1
                        break
                    else:
                        logger.error(f"  Parsing failed for page {page_no} (attempt {attempt + 1})")
                except requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code == 404:
                        logger.info(f"  Page {page_no} returned 404, no more pages.")
                        return total_saved
                    logger.warning(f"  HTTP error on page {page_no} (attempt {attempt + 1}): {e}")
                except Exception as e:
                    logger.warning(f"  Attempt {attempt + 1} failed for page {page_no}: {e}")

                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)

            if not success:
                logger.error(f"  Failed to fetch page {page_no} after {MAX_RETRIES} attempts, stopping category.")
                failed_record = {
                    "category_url": url,
                    "category_name": name,
                    "page_no": page_no,
                    "f_param": f_param,
                    "timestamp": datetime.now().isoformat(),
                }
                try:
                    self.failed_url_collection.insert_one(failed_record)
                except Exception:
                    pass
                break

            if not has_next:
                logger.info(f"  No more pages. Finished at page {page_no}.")
                break

            page_no += 1
            time.sleep(0.5)

        return total_saved

    def start(self):
        logger.info(f"Starting Jiomart crawler for {len(category_configs)} categories...")
        total_categories = 0
        for config in category_configs:
            try:
                saved = self.crawl_category(config)
                if saved:
                    total_categories += 1
            except Exception as e:
                logger.error(f"Error crawling category {config.get('name', config['url'])}: {e}")
        logger.info(f"Crawling complete. Processed {total_categories} categories.")

    def close(self):
        try:
            self.session.close()
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception:
            pass


if __name__ == "__main__":
    crawler_obj = Crawler()
    try:
        crawler_obj.start()
    finally:
        crawler_obj.close()
