import re
import json
import time
import random
import logging
import pymongo
import requests
from parsel import Selector
from pymongo import MongoClient

from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE,
    MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED,
    MONGO_RAW_RESPONSE_DB, MONGO_COLLECTION_RAW_RESPONSE,
    headers, cookies, EXTRACTION_DATE
)
from items import ProductDataItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GraingerParser:
    def __init__(self):
        self.headers = headers
        self.cookies = cookies

        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.raw_db = self.client[MONGO_RAW_RESPONSE_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.raw_collection = self.raw_db[MONGO_COLLECTION_RAW_RESPONSE]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]

        # Create unique index
        self.product_collection.create_index("url", unique=True)
        self.raw_collection.create_index("url", unique=True)
        logger.info("Connected to MongoDB")

    @staticmethod
    def get_nested(obj, path, default=None):
        for key in path:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return default
        return obj

    def fetch_page(self, url, max_retries=3):
        dynamic_headers = {**self.headers, "referer": "https://www.grainger.com/"}

        for attempt in range(max_retries):
            try:
                logger.info(f"  Fetching: {url} (Attempt {attempt + 1})...")
                response = requests.get(
                    url,
                    headers=dynamic_headers,
                    cookies=self.cookies,
                    timeout=30
                )

                if response.status_code == 200:
                    if 'script id="__PRELOADED_STATE__"' in response.text:
                        return response.text
                    else:
                        logger.warning(f"    Got 200 but __PRELOADED_STATE__ missing — possible block for {url}")
                        return None

                elif response.status_code == 404:
                    logger.error(f"    Product not found (404): {url}")
                    return None

                elif response.status_code == 403:
                    logger.warning(f"    Access denied (403) on attempt {attempt + 1}: {url}")

                else:
                    logger.error(f"    Failed [{response.status_code}] to fetch: {url}")

            except Exception as e:
                logger.warning(f"    Retryable error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(1, 3)
                logger.info(f"    Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)

        return None

  
    def parse_item(self, pdp_url, html_content):
        try:
            selector = Selector(text=html_content)
            script_text = selector.css('script#__PRELOADED_STATE__::text').get()
            if not script_text:
                logger.error(f"    __PRELOADED_STATE__ not found in HTML for {pdp_url}")
                return None

            data = json.loads(script_text)

            # Identify SKU
            sku = self.get_nested(data, ["product", "productDetails", "sku"])
            if not sku:
                logger.error(f"    Could not resolve SKU for {pdp_url}")
                return None

            product_details = self.get_nested(data, ["product", "productDetails"])
            gcom_products   = self.get_nested(data, ["product", "gcomProducts"]) or {}
            gcom_product    = gcom_products.get(sku) or (next(iter(gcom_products.values()), None) if gcom_products else None)
            config_data     = self.get_nested(data, ["product", "configData"]) or self.get_nested(data, ["configData"]) or self.get_nested(data, ["product", "configData", sku]) or {}

            #Manufacturer / Brand Name
            manufacturer_name = self.get_nested(product_details, ["external", "brandName"]) or ""
            brand_name = manufacturer_name

            #Manufacturer Part Number
            manufacturer_part_number = self.get_nested(product_details, ["manufacturerPartNumber"]) or ""

            # Vendor Seller Part Number
            vendor_seller_part_number = self.get_nested(product_details, ["sku"]) or ""

            # Item Name
            item_name = self.get_nested(config_data, ["digitalData", "page", "pageInfo", "contentTitle"]) or \
                        self.get_nested(config_data, ["digitalData", "productData", "productNm"]) or \
                        self.get_nested(product_details, ["primaryNoun"]) or ""
            # Full Product Description — Combine Description + Tech Specs
            raw_desc = self.get_nested(product_details, ["pdpDescription"]) or ""
            clean_desc = re.sub(r"<.*?>", "", raw_desc) # Strip HTML
            
            #specifications
            attr_strings = []
            attr_meta = product_details.get("attributes", [])
            attr_values = product_details.get("attributesById", {})
            for attr in attr_meta:
                name = attr.get("name")
                attr_id = str(attr.get("merchandisingAttributeId"))
                val_obj = attr_values.get(attr_id, {})
                
                if "values" in val_obj:
                    # Multi-value field (e.g. Features)
                    vals = [v.get("displayValue") for v in val_obj.get("values", []) if v.get("displayValue")]
                    value = "; ".join(vals)
                else:
                    value = val_obj.get("valueFormatted")
                
                if name and value:
                    attr_strings.append(f"{name}: {value}")
            
            specs_str = ", ".join(attr_strings)
            combined_desc = f"{clean_desc} {specs_str}".strip()
            
            full_product_description = " ".join(combined_desc.replace("\n", " ").split())

            # Price
            price = str(
                self.get_nested(gcom_product, ["hybrisProductInfo", "price", "sell", "price"])
                or self.get_nested(gcom_product, ["hybrisProductInfo", "price", "formattedPrice"])
                or ""
            )

            # Country of Origin
            country_of_origin = self.get_nested(config_data, ["productData", "countryOfOrigin"]) or ""

            # Unit of Issue (UOI)
            unit_of_issue = self.get_nested(gcom_product, ["hybrisProductInfo", "uomLabel"]) or ""

            # QTY Per UOI
            qty_per_uoi = str(self.get_nested(gcom_product, ["sellPackQty"]) or "")

            # Product Category
            ancestors = self.get_nested(product_details, ["ancestors"]) or []
            if ancestors:
                product_category = " > ".join([a.get("name", "") for a in ancestors if a.get("name")])
            else:
                product_category = self.get_nested(config_data, ["productData", "categoryName"]) or ""

            # Availability
            availability = self.get_nested(gcom_product, [
                "hybrisProductConfig", "view", "data", "productData", "priceDataMap", "product", "stockStatus"
            ]) or ""

            # Date Crawled
            date_crawled = EXTRACTION_DATE

         


            item = {
                "company_name":              "Grainger",
                "manufacturer_name":         manufacturer_name,
                "brand_name":                brand_name,
                "manufacturer_part_number":  manufacturer_part_number,
                "vendor_seller_part_number": vendor_seller_part_number,
                "item_name":                 item_name,
                "full_product_description":  full_product_description,
                "price":                     price,
                "country_of_origin":         country_of_origin,
                "unit_of_issue":             unit_of_issue,
                "qty_per_uoi":               qty_per_uoi,
                "upc":                       "",
                "model_number":              "",
                "product_category":          product_category,
                "url":                       pdp_url,
                "availability":              availability,
                "date_crawled":              date_crawled,
                "lead_time":                 "",
                "rohs_reach":                "",
                "stock_on_hand":             "",
            }

            try:
                # Save Raw Response
                raw_item = {
                    "url": pdp_url,
                    "html_content": html_content,
                    "extraction_date": EXTRACTION_DATE
                }
                self.raw_collection.update_one(
                    {"url": pdp_url},
                    {"$set": raw_item},
                    upsert=True
                )

                product_item = ProductDataItem(**item)
                product_item.validate()
                self.product_collection.insert_one(item)
                logger.info(f"    Saved: {pdp_url}")
            except pymongo.errors.DuplicateKeyError:
                logger.debug(f"    Duplicate (skipped): {pdp_url}")
            except Exception as e:
                logger.error(f"    Save error for {pdp_url}: {e}")

        except Exception as e:
            logger.error(f"    Error parsing {pdp_url}: {e}")
            return None

   
    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total URLs to process: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            pdp_url = doc.get("pdp_url")

            if not pdp_url:
                continue

            # De-duplicate
            if self.product_collection.find_one({"url": pdp_url}):
                logger.info(f"[{idx}/{total}] Already parsed, skipping: {pdp_url}")
                continue

            logger.info(f"[{idx}/{total}] Processing: {pdp_url}")

            html_content = self.fetch_page(pdp_url)

            if not html_content:
                logger.error(f"    Failed to fetch {pdp_url} — logging to failed collection")
                self.failed_url_collection.update_one(
                    {"url": pdp_url},
                    {"$set": {"pdp_url": pdp_url, "reason": "fetch_failed"}},
                    upsert=True
                )
                continue

            self.parse_item(pdp_url, html_content)
            time.sleep(random.uniform(1.5, 4.5))

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception:
            pass


if __name__ == "__main__":
    parser_obj = GraingerParser()
    try:
        parser_obj.start()
    except KeyboardInterrupt:
        logger.info("Parser stopped by user.")
    except Exception as e:
        logger.critical(f"Parser crashed: {e}")
    finally:
        parser_obj.close()
