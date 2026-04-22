import re
import pymongo
import time
import random
import json
import logging
import requests
from pymongo import MongoClient
from parsel import Selector

from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, 
    MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED,
    headers, EXTRACTION_DATE
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
        self.headers = headers
        
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]
        
        # Create indexes
        self.product_collection.create_index("url", unique=True)
        logger.info("Connected to MongoDB")

    def clean_description(self, text):
        if not text:
            return ""
        # Handle HD Supply specific caret separators first
        text = text.replace(' ^ ', '\n').replace('^', '\n')
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', ' ', text)
        # Normalize lines and whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    def fetch_page(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                logger.info(f"  Fetching: {url} (Attempt {attempt + 1})...")
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.error(f"    Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"    Failed [{response.status_code}] to fetch: {url}")
            
            except Exception as e:
                logger.warning(f"    Retryable error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(wait_time)
        
        return None

    def parse_item(self, pdp_url, html_content):
        try:
            selector = Selector(text=html_content)
            
            regex_pattern = r'catalogNavigationView\s*=\s*(\{.*?\})\s*-->'
            match = re.search(regex_pattern, html_content, re.DOTALL)
            if not match:
                regex_pattern = r'catalogNavigationView\s*=\s*(\{.*?\})'
                match = re.search(regex_pattern, html_content, re.DOTALL)
                
            if not match:
                logger.error(f"    Could not find JSON data for {pdp_url}")
                return None

            json_data = json.loads(match.group(1))
            if not json_data.get('catalogEntryView'):
                return None

            entry = json_data['catalogEntryView'][0]
            attributes = entry.get('attributes', [])

            # Helper to get attribute value by identifier
            def get_attr(identifier):
                for attr in attributes:
                    if attr.get('identifier') == identifier:
                        values = attr.get('values', [])
                        if values:
                            return str(values[0].get('value'))
                return ""

            rohs_reach = get_attr("Certifications & Standards")
            prop65_warning = get_attr("CaliforniaProp65WarningLabelText")
            if prop65_warning and prop65_warning.strip().upper().startswith("WARNING"):
                warning_text = prop65_warning.strip()
                if rohs_reach:
                    rohs_reach += f" | {warning_text}"
                else:
                    rohs_reach = warning_text
            # Clean description
            raw_description = entry.get('longDescription', '')
            description = self.clean_description(raw_description)

            # Price
            price_val = None
            if entry.get('price'):
                price_val = entry['price'][0].get('value')
            price = str(price_val) if price_val else ""

            manufacturer_name = entry.get('manufacturer', '')   
            manufacturer_part_number = entry.get('mfPartNumber_ntk', '') or get_attr("Manufacturer Part Number")
            vendor_part_number = entry.get('partNumber', '')
            item_name = entry.get('name', '')
            country_of_origin = get_attr("Country of Origin")
            unit_of_issue = get_attr("UOM")
            qty_per_uoi = get_attr("pkgquantity")
            upc = get_attr("UPC") or get_attr("Supplier UPC") or get_attr("UPC Code")
            model_number = "" # User explicitly requested empty for now
            availability = get_attr("MaterialStatus") or "Check Site"
            rohs_reach = rohs_reach

            breadcrumbs = selector.xpath('//div[@data-hds-tag="breadcrumbs"]//a[@data-hds-tag="breadcrumbs__breadcrumb-link"]/text()').getall()
            breadcrumb_path = " > ".join([a.strip() for a in breadcrumbs if a.strip()])
            
            item = {}
            item['company_name'] = 'HDSupplySolutions'
            item['manufacturer_name'] = manufacturer_name
            item['brand_name'] = manufacturer_name
            item['manufacturer_part_number'] = manufacturer_part_number
            item['vendor_seller_part_number'] = vendor_part_number
            item['item_name'] = item_name
            item['full_product_description'] = description
            item['price'] = price
            item['country_of_origin'] = country_of_origin
            item['unit_of_issue'] = unit_of_issue
            item['qty_per_uoi'] = qty_per_uoi
            item['upc'] = upc
            item['model_number'] = model_number
            item['product_category'] = breadcrumb_path
            item['url'] = pdp_url
            item['availability'] = availability
            item['date_crawled'] = EXTRACTION_DATE
            item['lead_time'] = ""
            item['rohs_reach'] = rohs_reach
            item['stock_on_hand'] = ""
            
            if item:
                try:
                    product_item = ProductDataItem(**item)
                    product_item.validate()
                    self.product_collection.insert_one(item)
                    logger.info(f"    Saved: {pdp_url}")
                except pymongo.errors.DuplicateKeyError:
                    pass
                except Exception as e:
                    logger.error(f"    Save error for {pdp_url}: {e}")
            else:
                logger.error(f"    Parsing failed for: {pdp_url}")

        except Exception as e:
            logger.error(f"    Error parsing {pdp_url}: {e}")
            return None

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        # Limit for initial run if needed, but here we process all
        for idx, doc in enumerate(self.url_collection.find(), 1):
            pdp_url = doc.get("pdp_url")
            
            if not pdp_url:
                continue

            # De-duplicate
            if self.product_collection.find_one({"url": pdp_url}):
                logger.info(f"Processing Item {idx}/{total}: {pdp_url} (Already exists, skipping)")
                continue

            logger.info(f"Processing Item {idx}/{total}: {pdp_url}")
            
            html_content = self.fetch_page(pdp_url)
            
            if not html_content:
                logger.error(f"    Failed to fetch {pdp_url}")
                self.failed_url_collection.update_one(
                    {"url": pdp_url},
                    {"$set": doc},
                    upsert=True
                )
                continue
            self.parse_item(pdp_url, html_content)

            time.sleep(random.uniform(0.5, 1.5))

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
    except Exception as e:
        logger.critical(f"Parser crashed: {e}")
    finally:
        parser_obj.close()
