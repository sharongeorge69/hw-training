import logging
import re
import pymongo
import time
import random
from curl_cffi import requests
from pymongo import MongoClient

from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_RAW_RESPONSE, MONGO_COLLECTION_URL_FAILED,
    headers_api, cookies,EXTRACTION_DATE
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
        self.headers = headers_api
        self.cookies = cookies
        
        # Use a session to persist cookies and connection
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)
        
        # PyMongo connection for reading and direct operations
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.raw_collection = self.db[MONGO_COLLECTION_RAW_RESPONSE]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        self.product_collection.create_index("unique_id", unique=True)
        self.raw_collection.create_index("unique_id", unique=True)
        logger.info("Connected to MongoDB")

    # def fetch_promotion_details(self, promo_id):
    #     """Fetch details for a specific promotion ID."""
    #     url = "https://apip.colruyt.be/gateway/ictmgmt.emarkecom.promotionretrsvc.v2/v2/nl/promotion"
    #     params = {
    #         'promotionIds': promo_id,
    #         'clientCode': 'CLP',
    #         'placeId': '604',
    #     }
        
    #     headers = {
    #         'accept': 'application/json, text/plain, */*',
    #         'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    #         'origin': 'https://www.colruyt.be',
    #         'priority': 'u=1, i',
    #         'referer': 'https://www.colruyt.be/',
    #         'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"Linux"',
    #         'sec-fetch-dest': 'empty',
    #         'sec-fetch-mode': 'cors',
    #         'sec-fetch-site': 'same-site',
    #         'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    #         'x-cg-apikey': 'a8ylmv13-b285-4788-9e14-0f79b7ed2411'
    #     }
        
    #     try:
    #         time.sleep(random.uniform(1.0, 2.0))
    #         resp = self.session.get(url, params=params, headers=headers, impersonate="chrome110", timeout=20)
    #         if resp.status_code == 200:
    #             return resp.json()
    #         else:
    #             logger.error(f"Failed [{resp.status_code}] to fetch promotion: {promo_id}")
    #     except Exception as e:
    #         logger.error(f"Error fetching promotion {promo_id}: {e}")
    #     return ""

    def fetch_product_details(self, tech_art_no):
        """Fetch full product details with retry logic."""
        url = "https://apip.colruyt.be/gateway/emec.cust.prdretr.extsvcv3/v3/nl/api/products/detail"
        params = {
            'placeId': '604',
            'clientCode': 'CLP',
            'ensignCountryCode': '8_BE',
            'technicalArtNo': tech_art_no,
            'dataGroup': 'ALL',
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(0.5, 1.5))
                resp = self.session.get(url, params=params, impersonate="chrome110", timeout=20)
                
                if resp.status_code == 200:
                    try:
                        return resp.json()
                    except ValueError as e:
                        logger.error(f"  JSON decode error for {tech_art_no} on attempt {attempt + 1}: {e}")
                else:
                    logger.error(f"  Failed [{resp.status_code}] to fetch product details for: {tech_art_no} (Attempt {attempt + 1})")
            
            except (requests.errors.Timeout, requests.errors.RequestError) as e:
                logger.warning(f"  Retryable error for {tech_art_no} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 * (attempt + 1) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                logger.error(f"  Max retries reached for product details: {tech_art_no}")
        
        return ""


    def start(self):
        """Read crawler payload from MongoDB and parse each item."""
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            technical_article_number = doc.get("technicalArticleNumber")
            # tech_promo_id = doc.get("techPromoId")
            commercial_article_number = doc.get("commercialArticleNumber")
            if not technical_article_number:
                logger.warning(f"Item {idx}/{total} is missing technicalArticleNumber. Skipping.")
                continue

            unique_id = str(commercial_article_number)

            if self.product_collection.find_one({"unique_id": unique_id}):
                logger.debug(f"Skipped already parsed: {unique_id}")
                continue

            logger.info(f"Processing Item {idx}/{total}: {unique_id}")
            
            # 1. Fetch Product Details
            product_details = self.fetch_product_details(technical_article_number)
            
            if not product_details:
                logger.error(f"Skipping {unique_id} because all retries failed.")
                # Add to failed collection
                self.failed_url_collection.update_one(
                    {"unique_id": unique_id},
                    {"$set": doc},
                    upsert=True
                )
                continue

            # 2. Fetch Promotion Details (if applicable)
            # promotion_details = ""
            # if tech_promo_id:
            #     promotion_details = self.fetch_promotion_details(tech_promo_id)
                
            # 3. Aggregate data and save
            self.parse_item(unique_id, doc, product_details)

    def parse_item(self, unique_id, payload, product_details):

        content = payload.get('content', '')
        pdp_url = str(payload.get('pdp_url', ''))
        is_available = str(payload.get('isAvailable', ''))
        pub_start = str(payload.get('publicationStartDate', ''))
        pub_end = str(payload.get('publicationEndDate', ''))
        full_image = str(payload.get('fullImage', ''))

        measurement_unit_quantity_price = str(payload.get('measurementUnitQuantityPrice', ''))
        measurement_unit_price_payload = str(payload.get('measurementUnitPrice', ''))
        measurement_unit = str(payload.get('measurementUnit', ''))
        price_per_uom = str(payload.get('pricePerUOM', ''))
        tech_promo_id = str(payload.get('techPromoId', ''))
        promotion_id = str(payload.get('promotionId', ''))

        name = product_details.get("name", "")
        brand = product_details.get("brand", "")
        detail_desc_raw = product_details.get("description", "")
        detail_origin = str(product_details.get('CountryOfOrigin', ''))
        categories = product_details.get("categories", [])
        allergens_data = product_details.get("allergenAttributes", {})

        #product name
        product_name = f"{brand} {name}".strip()
        
        # Grammage extraction
        grammage_quantity = ""
        grammage_unit = ""
        match = re.match(r'([\d,\.]+)([a-zA-Z]+)', content)
        if match:
            grammage_quantity = match.group(1).replace(',', '.')
            grammage_unit = match.group(2).lower()

        # Hierarchy & Breadcrumb
        levels = []
        node = categories[0] if categories else None
        while node:
            levels.append(node.get("name"))
            children = node.get("children")
            node = children[0] if children else None
        
        levels.append(f"{brand} {name}".strip())
        breadcrumb = " > ".join(levels) if levels else ""

        # Price processing
        basic_price = ""
        quantity_price = ""
        quantity_price_quantity = ""
        measurement_unit_price = ""
        
        #price details
        price_dict = product_details.get('price', {})
        basic_price = price_dict.get('basicPrice', '')
        quantity_price = price_dict.get('quantityPrice', '')
        quantity_price_quantity = price_dict.get('quantityPriceQuantity', '')
        measurement_unit_price = price_dict.get('measurementUnitPrice', '')

        regular_price = str(basic_price)
        selling_price = regular_price
        price_per_unit = str(measurement_unit_price)

        # Description cleaning
        description = ", ".join(
            re.sub(r'^[\*\-\•]\s*', '', d).strip()
            for d in detail_desc_raw.split("\n")
            if d.strip()
        )

        # Allergens processing
        allergens_list = []
        for key, value in allergens_data.items():
            if value == "CONTAINS":
                allergen = key.replace("AllergenDetails", "").capitalize()
                allergens_list.append(allergen)
        allergens = ", ".join(allergens_list)

        # Promotion description
        promotion_description = ""
        if quantity_price:
            promotion_description = f"{quantity_price} vanaf {quantity_price_quantity} st"

        # 4. Dictionary Assignment
        item = {}
        item['unique_id'] = unique_id
        item['product_unique_key'] = f"{unique_id}P"
        item['competitor_name'] = "colruyt"
        item['extraction_date'] = EXTRACTION_DATE
        item['product_name'] = product_name
        item['brand'] = brand
        item['grammage_quantity'] = grammage_quantity
        item['grammage_unit'] = grammage_unit
        item['breadcrumb'] = breadcrumb
        item['pdp_url'] = pdp_url
        item['regular_price'] = regular_price
        item['selling_price'] = selling_price
        item['promotion_valid_from'] = pub_start
        item['promotion_valid_upto'] = pub_end
        item['price_valid_from'] = pub_start
        item['price_per_unit'] = price_per_unit
        item['currency'] = "EUR"
        item['product_description'] = description
        item['image_url_1'] = full_image
        item['file_name_1'] = ""
        item['instock'] = is_available
        item['country_of_origin'] = detail_origin
        item['allergens'] = allergens
        item['promotion_description'] = promotion_description
        item['site_shown_uom'] = content
        
        # Base crawler fields
        item['measurementUnitQuantityPrice'] = measurement_unit_quantity_price
        item['measurementUnitPrice'] = measurement_unit_price_payload
        item['measurementUnit'] = measurement_unit
        item['pricePerUOM'] = price_per_uom
        item['techPromoId'] = tech_promo_id
        item['promotionId'] = promotion_id
        
        # Map hierarchy levels
        for i, value in enumerate(levels, start=1):
            if i <= 10:
                item[f"producthierarchy_level{i}"] = value

        try:
            # 5. Save Raw Response
            if product_details:
                raw_item = {
                    "unique_id": unique_id,
                    "product_details": product_details,
                    "extraction_date": EXTRACTION_DATE
                }
                self.raw_collection.update_one(
                    {"unique_id": unique_id},
                    {"$set": raw_item},
                    upsert=True
                )
                logger.info(f"    Raw saved: {unique_id}")

            # Instantiate MongoEngine document (schema validation only)
            product_item = ProductDataItem(**item)
            product_item.validate()
            # Insert dict via pymongo
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
