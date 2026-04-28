import re
import json
import time
import requests
import random
import pymongo
import logging
from pymongo import MongoClient

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

    def find_matching_brace(self, s, start_index):
        count = 0
        for i in range(start_index, len(s)):
            if s[i] == '{':
                count += 1
            elif s[i] == '}':
                count -= 1
                if count == 0:
                    return i
        return -1

    def get_product_detail(self, product_details, name):
        if not isinstance(product_details, list):
            return None
        for detail in product_details:
            if detail.get('name', '').lower() == name.lower():
                return detail.get('value')
        return None

    def fetch_page(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.error(f"    Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"    Failed [{response.status_code}] to fetch: {url}")
            except Exception as e:
                logger.warning(f"    Retryable error for {url} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                logger.error(f"    Max retries reached for: {url}")
        
        return None

    def extract_data_from_html(self, html_content):
        # SKUPAGE_INITIAL_STATE extraction
        data = {}
        start_match = re.search(r'window\.SKUPAGE_INITIAL_STATE\s*=\s*\{', html_content)
        if start_match:
            brace_start = start_match.end() - 1
            brace_end = self.find_matching_brace(html_content, brace_start)
            if brace_end != -1:
                js_obj_str = html_content[brace_start:brace_end+1]
                clean_json_str = re.sub(r':\s*undefined([,}])', r': null\1', js_obj_str)
                try:
                    data = json.loads(clean_json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding initial state JSON: {e}")

        # dataLayer extraction
        datalayer_data = {}
        try:
            start_match_dl = re.search(r'window\.dataLayer\.push\(\s*\{\s*"event"\s*:\s*"onPageRendered"', html_content)
            if start_match_dl:
                brace_start = html_content.find('{', start_match_dl.start())
                brace_end = self.find_matching_brace(html_content, brace_start)
                if brace_end != -1:
                    dl_obj_str = html_content[brace_start:brace_end+1]
                    clean_dl_str = re.sub(r':\s*undefined([,}])', r': null\1', dl_obj_str)
                    datalayer_data = json.loads(clean_dl_str)
        except Exception as e:
             logger.error(f"Error extracting dataLayer: {e}")

        return {
            "sku_state": data,
            "datalayer": datalayer_data
        }

    def clean_description(self, text):
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def parse_item(self, data_wrapper, url):
        data = data_wrapper.get('sku_state', {})
        datalayer = data_wrapper.get('datalayer', {})
        
        query = data.get('query', {})
        fetch_data = data.get('fetchData', {})
        sku_info = fetch_data.get('skuInfo', {})
        catalog = sku_info.get('catalog', {})
        sku_details = sku_info.get('skuDetails', {})
        product_details = catalog.get('productDetails', [])
        breadcrumbs = catalog.get('breadcrumbs', [])
        price_info = sku_details.get('price', {})

        # Manufacturer Name
        manufacturer_name = self.get_product_detail(product_details, 'manufacturer') or catalog.get('brand')
        
        # Brand Name
        brand_name = catalog.get('brand')
        
        # Manufacturer Part Number
        mfg_part_num = sku_details.get('mfgId')
        
        # Vendor Seller Part Number
        vendor_part_num = query.get('skuId') or sku_details.get('skuId')
        
        # Item Name
        item_name = catalog.get('title')
        
        # Full Product Description
        desc_header = catalog.get('descriptionHeader', '')
        desc_bullets = catalog.get('descriptionBullets', [])
        full_description = desc_header + " " + " ".join(desc_bullets) if desc_bullets else desc_header
        
        full_description = self.clean_description(full_description)
        
        # Price
        price = price_info.get('sellPrice', {}).get('price')
        
        # Country of Origin
        country_of_origin = self.get_product_detail(product_details, 'Country of Origin') or ""
        
        # Unit of Issue (UOI)
        uoi = sku_details.get('uom') or "each"
        
        # QTY Per UOI
        qty_per_uoi = (
            self.get_product_detail(product_details, 'Quantity')
            or self.get_product_detail(product_details, 'Total Quantity')
            or self.get_product_detail(product_details, 'Pack Size')
            or "1"
        )
        
        # UPC
        upc = catalog.get('upc') or self.get_product_detail(product_details, 'UPC')
        
        # Model Number
        model_number = self.get_product_detail(product_details, 'model')
        
        # Product Category
        product_category = " > ".join([bc.get('description', '') for bc in breadcrumbs if bc.get('description')]) if breadcrumbs else "N/A"
        
        # Availability
        availability = ""
        product_dl = datalayer.get('product', {})
        dl_out_of_stock = product_dl.get('is_out_of_stock')
        
        if dl_out_of_stock is not None:
            availability = "Out of Stock" if dl_out_of_stock else "In Stock"
      
        # Stock on Hand
        stock_on_hand = ""
        dl_available_qty = product_dl.get('available_qty')
        if dl_available_qty is not None and str(dl_available_qty).strip() != "":
            stock_on_hand = str(dl_available_qty)

        # Lead Time
        lead_time = sku_details.get('deliveryMessage', '')

        # Dictionary Assignment
        item = {}
        item['company_name'] = "OfficeDepot"
        item['manufacturer_name'] = str(manufacturer_name or "").strip()
        item['brand_name'] = str(brand_name or "").strip()
        item['manufacturer_part_number'] = str(mfg_part_num or "").strip()
        item['vendor_seller_part_number'] = str(vendor_part_num or "").strip()
        item['item_name'] = str(item_name or "").strip()
        item['full_product_description'] = str(full_description).strip()
        item['price'] = str(price or "").strip()
        item['country_of_origin'] = str(country_of_origin or "").strip()
        item['unit_of_issue'] = str(uoi or "").strip()
        item['qty_per_uoi'] = str(qty_per_uoi or "").strip()
        item['upc'] = str(upc or "").strip()
        item['model_number'] = str(model_number or "").strip()
        item['product_category'] = str(product_category or "").strip()
        item['url'] = str(url).strip()
        item['availability'] = str(availability or "").strip()
        item['date_crawled'] = str(EXTRACTION_DATE)
        item['lead_time'] = str(lead_time or "").strip()
        item['rohs_reach'] = ""
        item['stock_on_hand'] = str(stock_on_hand or "").strip()
        
        try:
            # Schema validation and save
            product_item = ProductDataItem(**item)
            product_item.validate()
            self.product_collection.insert_one(item)
            logger.info(f"    Saved: {url}")
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"    Skipped duplicate: {url}")
        except Exception as e:
            logger.error(f"    Save error for {url}: {e}")

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            pdp_url = doc.get("pdp_url")
            
            if not pdp_url:
                continue

            if self.product_collection.find_one({"url": pdp_url}):
                logger.info(f"Processing Item {idx}/{total}: {pdp_url} (Already parsed)")
                continue

            base_url = pdp_url.split('#')[0]

            logger.info(f"Processing Item {idx}/{total}: {base_url}")
            
            html_content = self.fetch_page(base_url)
            
            if not html_content:
                logger.error(f"    Skipping {base_url} because fetching failed.")
                self.failed_url_collection.update_one(
                    {"pdp_url": pdp_url},
                    {"$set": doc},
                    upsert=True
                )
                continue

            data_wrapper = self.extract_data_from_html(html_content)
            
            if data_wrapper and data_wrapper.get("sku_state"):
                self.parse_item(data_wrapper, pdp_url)
            else:
                logger.error(f"    Failed to extract JSON state for {pdp_url}")
                self.failed_url_collection.update_one(
                    {"pdp_url": pdp_url},
                    {"$set": doc},
                    upsert=True
                )

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
