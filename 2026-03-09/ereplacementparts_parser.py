import logging
import pymongo
from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE,
    MONGO_COLLECTION_DATA,
    headers_parser
)
from items import ProductDataItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Parser:

    def __init__(self):
        self.headers = headers_parser

        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.product_collection.create_index("input_part_number", unique=True)
        logger.info("Connected to MongoDB")

    def get_compatible_products(self, pdp_url: str, inventory_id: str) -> str:
        """Paginate the ModelCrossReference API to collect all compatible model numbers."""
        # XPATH — API returns bare <tr> fragments 
        COMPAT_API_XPATH = "//tr/td[2]/a/text()"

        models = []
        page = 2  # Page 1 is already embedded in the PDP HTML
        while True:
            api_url = f"{pdp_url}?currentPage={page}&inventoryID={inventory_id}&handler=ModelCrossReference&"
            try:
                resp = requests.get(api_url, headers=self.headers, impersonate="chrome110", timeout=20)
                if resp.status_code != 200:
                    break

                # EXTRACT
                sel = Selector(text=resp.text)
                rows = sel.xpath(COMPAT_API_XPATH).extract()
                if not rows:
                    break
                models.extend(rows)
                page += 1
            except Exception as e:
                logger.error(f"Compatible products API error page {page}: {e}")
                break
        return models

    def start(self):
        """Read PDP URLs from MongoDB and parse each one."""
        total = self.url_collection.count_documents({})
        logger.info(f"Total PDPs to process: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            pdp_url = doc.get("pdp_url")
            if not pdp_url:
                continue

            if self.product_collection.find_one({"url": pdp_url}):
                logger.debug(f"Skipped already parsed: {pdp_url}")
                continue

            logger.info(f"Item {idx}/{total}: {pdp_url}")
            try:
                response = requests.get(pdp_url, headers=self.headers, impersonate="chrome110", timeout=30)
                if response.status_code == 200:
                    self.parse_item(response, pdp_url)
                else:
                    logger.error(f"Failed [{response.status_code}]: {pdp_url}")
            except Exception as e:
                logger.error(f"Error fetching {pdp_url}: {e}")

    def parse_item(self, response, pdp_url: str):
        """Parse a single PDP page and save to MongoDB."""
        sel = Selector(text=response.text)

        # XPATH
        TITLE_XPATH = '//h1[@itemprop="name"]//text()'
        MANUFACTURER_XPATH = '//dd[@itemprop="brand"]//span[@itemprop="name"]//text()'
        PRICE_XPATH = '//span[@itemprop="price"]//text()'
        DESCRIPTION_XPATH = '//p[@itemprop="description"]//text()'
        AVAILABILITY_XPATH = '//span[@itemprop="availability"]//text()'
        PART_NUMBER_XPATH = "//dt[normalize-space()='Part Number:']/following-sibling::dd[1]/text()"
        IMAGE_XPATH = ('//div[@class="pd__img"]//a/@href')
        EQUIV_PARTS_XPATH = (
            "//div[@id='Troubleshooting']//div[contains(normalize-space(),'replaces these')]"
            "/following-sibling::ul[1]/li//text()"
        )
        COMPATIBLE_ROWS_XPATH = "//tbody//tr/td[2]/a/text()"
        INVENTORY_ID_XPATH    = "//div[@data-handler='ModelCrossReference']/@data-inventory-id"

        # EXTRACT
        title = sel.xpath(TITLE_XPATH).extract_first("").strip()
        manufacturer = sel.xpath(MANUFACTURER_XPATH).extract_first("").strip()
        price = sel.xpath(PRICE_XPATH).extract_first("").strip()
        description = sel.xpath(DESCRIPTION_XPATH).extract_first("").strip()
        availability = sel.xpath(AVAILABILITY_XPATH).extract_first("").strip()
        input_part_number = sel.xpath(PART_NUMBER_XPATH).extract_first("").strip()

        # Image URLs - comma separated
        raw_images = sel.xpath(IMAGE_XPATH).extract()
        image_urls = ", ".join(list(dict.fromkeys(img for img in raw_images if img.startswith("http"))))

        # Equivalent part numbers - comma separated
        equiv_list = sel.xpath(EQUIV_PARTS_XPATH).extract()
        equivalent_part_numbers = ", ".join(e.strip() for e in equiv_list if e.strip())

        # Compatible products — page 1 from PDP HTML + remaining pages via API
        inventory_id = sel.xpath(INVENTORY_ID_XPATH).extract_first()
        page1_models = sel.xpath(COMPATIBLE_ROWS_XPATH).extract()
        extra_models = self.get_compatible_products(pdp_url, inventory_id) if inventory_id else []
        compatible_products = ", ".join(page1_models + extra_models)



        item = {
            "input_part_number": input_part_number,
            "url": pdp_url,
            "title": title,
            "manufacturer": manufacturer,
            "price": price,
            "description": description,
            "oem_part_number": "",
            "retailer_part_number": "",
            "competitor_part_numbers": "",
            "compatible_products": compatible_products,
            "equivalent_part_numbers": equivalent_part_numbers,
            "product_specifications": "",
            "additional_description": "",
            "availability": availability,
            "image_urls": image_urls,
            "linked_files": "",
        }

        try:
            product_item = ProductDataItem(**item)
            product_item.validate()
            self.product_collection.insert_one(item)
            logger.info(f"Saved: {pdp_url}")
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"Skipped duplicate: {pdp_url}")
        except Exception as e:
            logger.error(f"Save error for {pdp_url}: {e}")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass


if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()
