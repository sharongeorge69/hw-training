import re
import pymongo
import time
import random
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_RAW_RESPONSE, MONGO_COLLECTION_URL_FAILED,
    headers, EXTRACTION_DATE
)
from items import ProductDataItem

# Configure Logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.headers = headers
        
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.raw_collection = self.db[MONGO_COLLECTION_RAW_RESPONSE]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        
        # Create indexes
        self.product_collection.create_index("unique_id", unique=True)
        self.raw_collection.create_index("unique_id", unique=True)
        logger.info("Connected to MongoDB")

    def fetch_product_details(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:                
                resp = requests.get(url, headers=self.headers, timeout=20)
                
                if resp.status_code == 200:

                    return resp.text
                elif resp.status_code == 404:
                    logger.error(f"  Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"  Failed [{resp.status_code}] to fetch: {url} (Attempt {attempt + 1})")
            
            except Exception as e:
                logger.warning(f"  Retryable error for {url} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 * (attempt + 1) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                logger.error(f"  Max retries reached for: {url}")
        
        return None

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            pdp_url = doc.get("pdp_url")
            product_id = doc.get("product_id")
            
            if not pdp_url or not product_id:
                logger.warning(f"Item {idx}/{total} is missing data. Skipping.")
                continue

            unique_id = str(product_id)

            # De-duplicate
            if self.product_collection.find_one({"unique_id": unique_id}):
                logger.debug(f"Skipped already parsed: {unique_id}")
                continue

            logger.info(f"Processing Item {idx}/{total}: {unique_id}")
            
            html_content = self.fetch_product_details(pdp_url)
            
            if not html_content:
                logger.error(f"Skipping {unique_id} because fetching failed.")
                self.failed_url_collection.update_one(
                    {"unique_id": unique_id},
                    {"$set": doc},
                    upsert=True
                )
                continue

            self.parse_item(pdp_url, unique_id, html_content)

    def parse_item(self, pdf_url, unique_id, html_content):
        sel = Selector(text=html_content)
        
        # XPaths
        BRAND_XPATH = "normalize-space(//span[contains(@class,'mod-article-intro__header-headline-small')])"
        PRODUCT_NAME_XPATH = "normalize-space(//div[contains(@class,'mod-article-intro__header-headline')]//h1/text()[normalize-space()])"
        SITE_SHOWN_UOM_XPATH = "normalize-space(//span[contains(@class,'price__unit')])"
        PRICE_PER_UNIT_XPATH = "normalize-space(//span[contains(@class,'price__base')])"
        PRODUCT_DESCRIPTION_XPATH = "normalize-space(//div[contains(@class,'rte')]//p)"
        REGULAR_PRICE_XPATH = "normalize-space(//s[contains(@class,'price__previous')])"
        SELLING_PRICE_XPATH = "normalize-space(//span[contains(@class,'price__wrapper')])"
        IMAGE_XPATH = "//div[contains(@class,'mod-gallery-article__stage')]//a[contains(@class,'has-lightbox')]/@href"
        PROMOTION_DESCRIPTION_XPATH = "normalize-space(//div[contains(@class,'price')]//span[contains(@class,'price__previous-percentage')])"

        # Basic Fields
        product_name = sel.xpath(PRODUCT_NAME_XPATH).extract_first()
        brand = sel.xpath(BRAND_XPATH).extract_first()
        product_unique_key = f"{unique_id}P"
        currency = "EUR"
        competitor_name = "aldi"
        site_shown_uom = sel.xpath(SITE_SHOWN_UOM_XPATH).extract_first()
        price_per_unit = sel.xpath(PRICE_PER_UNIT_XPATH).extract_first()
        
        # Clean price_per_unit
        if price_per_unit:
            match = re.search(r'([\d,.]+)', price_per_unit)
            if match:
                price_per_unit = match.group(1)

        product_description = sel.xpath(PRODUCT_DESCRIPTION_XPATH).extract_first()
        promotion_description = sel.xpath(PROMOTION_DESCRIPTION_XPATH).extract_first()
        pdp_url = pdf_url

        # Grammage Logic
        grammage_quantity = ""
        grammage_unit = ""
        if site_shown_uom:
            parts = site_shown_uom.rsplit(None, 1)
            if len(parts) == 2:
                grammage_quantity = parts[0].strip()
                grammage_unit = parts[1].strip()
            else:
                grammage_quantity = site_shown_uom

        # Price Logic
        regular_price = sel.xpath(REGULAR_PRICE_XPATH).extract_first()
        selling_price = sel.xpath(SELLING_PRICE_XPATH).extract_first()
        
        price_was = ""
        if regular_price:
            regular_price = regular_price
            selling_price = selling_price
            price_was = regular_price
        else:
            regular_price = selling_price
            selling_price = selling_price
            price_was = ""

        # Breadcrumb logic
        level1 = "STARTPAGINA"
        level2 = "PRODUCTEN"
        level3 = "ASSORTIMENT"
        level4 = "ALCOHOLVRIJE DRANKEN"
        
        # Level 5 from URL
        level5 = ""
        if "limonades" in pdp_url.lower():
            level5 = "LIMONADES"
        elif "energy-drinks-sportdrank" in pdp_url.lower():
            level5 = "ENERGY DRINKS EN SPORTDRANK"
        else:
            # Fallback/Default handling for other categories
            if "#" in pdp_url:
                hash_part = pdp_url.split("#")[1]
                last_slug = hash_part.strip("/").split("/")[-1]
                level5 = last_slug.replace("-", " ").upper()

        level6 = str(product_name).upper() if product_name else ""
        
        # Construct Breadcrumb
        breadcrumb_parts = [level1, level2, level3, level4, level5, level6]
        breadcrumb = " > ".join([p for p in breadcrumb_parts if p])

        # Image processing
        raw_images = sel.xpath(IMAGE_XPATH).extract()
        image_urls = []
        for img in raw_images:
            if img.startswith("/"):
                image_urls.append(f"https://www.aldi.be{img}")
            else:
                image_urls.append(img)

        # Dictionary Assignment
        item = {}
        item['unique_id'] = unique_id
        item['competitor_name'] = competitor_name
        item['extraction_date'] = EXTRACTION_DATE
        item['product_name'] = product_name
        item['brand'] = brand
        item['grammage_quantity'] = grammage_quantity
        item['grammage_unit'] = grammage_unit
        item['product_unique_key'] = product_unique_key
        item['currency'] = currency
        item['site_shown_uom'] = site_shown_uom
        item['price_per_unit'] = price_per_unit
        item['product_description'] = product_description
        item['breadcrumb'] = breadcrumb
        item['pdp_url'] = pdp_url
        item['regular_price'] = regular_price
        item['selling_price'] = selling_price
        item['price_was'] = price_was
        item['promotion_description'] = promotion_description

        # Map multiple images
        for i, url in enumerate(image_urls, start=1):
            if i <= 6:
                item[f'image_url_{i}'] = url    

        # Map hierarchy levels (Hardcoded)
        item['producthierarchy_level1'] = level1
        item['producthierarchy_level2'] = level2
        item['producthierarchy_level3'] = level3
        item['producthierarchy_level4'] = level4
        item['producthierarchy_level5'] = level5
        item['producthierarchy_level6'] = level6
        
        try:
            # Save Raw Response
            # raw_item = {
            #     "unique_id": unique_id,
            #     "html_content": html_content,
            #     "extraction_date": EXTRACTION_DATE
            # }
            # self.raw_collection.update_one(
            #     {"unique_id": unique_id},
            #     {"$set": raw_item},
            #     upsert=True
            # )

            # Schema validation and save
            product_item = ProductDataItem(**item)
            product_item.validate()
            self.product_collection.insert_one(item)
            logger.info(f"    Saved: {unique_id}")
            
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"    Skipped duplicate: {unique_id}")
        except Exception as e:
            logger.error(f"    Save error for {unique_id}: {e}")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    parser_obj = Parser()
    try:
        parser_obj.start()
    finally:
        parser_obj.close()
