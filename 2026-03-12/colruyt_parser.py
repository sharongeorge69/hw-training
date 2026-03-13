import logging
import re
import json
import pymongo
import time
import random
from curl_cffi import requests
from pymongo import MongoClient

from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
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
        self.product_collection.create_index("unique_id", unique=True)
        logger.info("Connected to MongoDB")

    def fetch_promotion_details(self, promo_id):
        """Fetch details for a specific promotion ID."""
        url = "https://apip.colruyt.be/gateway/ictmgmt.emarkecom.promotionretrsvc.v2/v2/nl/promotion"
        params = {
            'promotionIds': promo_id,
            'clientCode': 'CLP',
            'placeId': '604',
        }
        
        # Promotion API seems to prefer these exact headers
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
            'origin': 'https://www.colruyt.be',
            'priority': 'u=1, i',
            'referer': 'https://www.colruyt.be/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'x-cg-apikey': 'a8ylmv13-b285-4788-9e14-0f79b7ed2411'
        }
        
        try:
            time.sleep(random.uniform(1.0, 2.0))
            resp = self.session.get(url, params=params, headers=headers, impersonate="chrome110", timeout=20)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.error(f"Failed [{resp.status_code}] to fetch promotion: {promo_id}")
        except Exception as e:
            logger.error(f"Error fetching promotion {promo_id}: {e}")
        return ""

    def fetch_product_details(self, tech_art_no):
        """Fetch full product details."""
        url = "https://apip.colruyt.be/gateway/emec.cust.prdretr.extsvcv3/v3/nl/api/products/detail"
        params = {
            'placeId': '604',
            'clientCode': 'CLP',
            'ensignCountryCode': '8_BE',
            'technicalArtNo': tech_art_no,
            'dataGroup': 'ALL',
        }
        
        try:
            time.sleep(random.uniform(0.5, 1.5))
            resp = self.session.get(url, params=params, impersonate="chrome110", timeout=20)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.error(f"Failed [{resp.status_code}] to fetch product details for: {tech_art_no}")
        except Exception as e:
            logger.error(f"Error fetching product details {tech_art_no}: {e}")
        return ""


    def start(self):
        """Read crawler payload from MongoDB and parse each item."""
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            technical_article_number = doc.get("technicalArticleNumber")
            tech_promo_id = doc.get("techPromoId")
            commercial_article_number = doc.get("commercialArticleNumber")
            # Use technicalArticleNumber as our unique primary key for the API payload
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
            
            # 2. Fetch Promotion Details (if applicable)
            promotion_details = ""
            if tech_promo_id:
                promotion_details = self.fetch_promotion_details(tech_promo_id)
                
            # 3. Aggregate data and save
            self.parse_item(unique_id, doc, product_details, promotion_details)

    def parse_item(self, unique_id, payload, product_details, promotion_details):
        

        brand = payload.get('brand', '')
        name = payload.get('name', '')
        product_name = f"{brand} {name}" 
        content = payload.get('content', '')
        grammage_quantity = ""
        grammage_unit = ""
        match = re.match(r'([\d,\.]+)([a-zA-Z]+)', content)
        if match:
            grammage_quantity = match.group(1) 
            grammage_unit = match.group(2)

        #producthierarchy
        categories = product_details.get("categories", [])
        name = product_details.get("name", "") 
        brand = product_details.get("brand", "")
        
        levels = []              
        
        node = categories[0] if categories else None
        
        # Traverse category hierarchy                                                                    
        while node:            
            levels.append(node.get("name"))
            children = node.get("children")         
            node = children[0] if children else None
        
        levels.append(f"{brand} {name}")   
                                        
        # Assign to producthierarchy levels         
        producthierarchy = {}
        
        for i, value in enumerate(levels, start=1):
            producthierarchy[f"producthierarchy_level{i}"] = value                                 

        # Build breadcrumb string
        breadcrumb = " > ".join(levels) if levels else ""
        regular_price = str(payload.get('basicPrice', ''))
        selling_price = regular_price
        promotion_valid_from = str(payload.get('publicationStartDate', ''))
        promotion_valid_upto = str(payload.get('publicationEndDate', ''))
        price_valid_from = promotion_valid_from
        price_per_unit = str(payload.get('measurementUnitPrice', ''))
        #product description
        description_raw = product_details.get("description", "")
        description = ", ".join(
            re.sub(r'^[\*\-\•]\s*', '', d).strip()
            for d in description_raw.split("\n")
            if d.strip()
        )
        image_url_1 = str(payload.get('fullImage', ''))
        country_of_origin = str(product_details.get('countryOfOrigin', ''))
        #allergens
        allergens_data = product_details.get("allergenAttributes", {})
        allergens = []

        for key, value in allergens_data.items():
            if value == "CONTAINS":
                allergen = key.replace("AllergenDetails", "")
                allergen = allergen.capitalize()
                allergens.append(allergen)

        allergens = ", ".join(allergens)

        item = {
            "unique_id": unique_id,
            "product_unique_key": f"{unique_id}P",
            "competitor_name": "colruyt",
            "extraction_date": EXTRACTION_DATE,
            "product_name": product_name,
            "brand": brand,
            "grammage_quantity": grammage_quantity,
            "grammage_unit": grammage_unit,
            "breadcrumb": breadcrumb,
            "pdp_url": str(payload.get('pdp_url', '')),
            "regular_price": regular_price,
            "selling_price": selling_price,
            "promotion_valid_from": promotion_valid_from if promotion_valid_from else "",
            "promotion_valid_upto": promotion_valid_upto if promotion_valid_upto else "",
            "price_valid_from": price_valid_from if price_valid_from else "",
            "price_per_unit": price_per_unit if price_per_unit else "",
            "currency": "euro",
            "product_description": description,
            "image_url_1": image_url_1,
            "file_name_1":"",
            "isAvailable": str(payload.get('isAvailable', '')),
            "country_of_origin": country_of_origin,
            "allergens": allergens,
            # Include base crawler payload

         
            "recommendedQuantity": str(payload.get('recommendedQuantity', '')),
            "quantityPrice": str(payload.get('quantityPrice', '')),
            "quantityPriceQuantity": str(payload.get('quantityPriceQuantity', '')),
            "measurementUnitQuantityPrice": str(payload.get('measurementUnitQuantityPrice', '')),
            "measurementUnitPrice": str(payload.get('measurementUnitPrice', '')),
            "measurementUnit": str(payload.get('measurementUnit', '')),
            "pricePerUOM": str(payload.get('pricePerUOM', '')),
            "isAvailable": str(payload.get('isAvailable', '')),
            "countryOfOrigin": str(payload.get('countryOfOrigin', '')),
            "techPromoId": str(payload.get('techPromoId', '')),
            "promotionId": str(payload.get('promotionId', '')),
            "promotionType": str(payload.get('promotionType', '')),

            
            # Appended detail JSON
            "product_details": json.dumps(product_details),
            "promotion_details": json.dumps(promotion_details)
        }
        
        # Map hierarchy levels
        for i, value in enumerate(levels, start=1):
            if i <= 10:
                item[f"producthierarchy_level{i}"] = value

        try:
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
