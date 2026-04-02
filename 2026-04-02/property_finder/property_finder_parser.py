import logging
import time
import json
import re
import urllib.parse
import requests
from pymongo import MongoClient
import pymongo

# Local
from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA,
    EXTRACTION_DATE, SLICER_PROPERTY_TYPES, SLICER_BEDROOMS,
    SLICER_PRICES, SLICER_AREAS
)
from items import LocationItem, TransactionItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.period = "3y"
        self.max_results_limit = 500
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.transactions_collection = self.db[MONGO_COLLECTION_DATA]

        logger.info("Connected to MongoDB")
        
        self.build_id = self.get_build_id()
        if not self.build_id:
            logger.error("Failed to initialize build ID. Exiting.")
            return

    def get_build_id(self):
        url = "https://www.propertyfinder.ae/en/transactions/rent/dubai"
        logger.info(f"Extracting buildId from {url}...")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to load initial page: Code {response.status_code}")
                return None
            
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
            if not match:
                logger.error("Could not find __NEXT_DATA__")
                return None
            
            data = json.loads(match.group(1))
            build_id = data.get("buildId")
            logger.info(f"Extracted buildId: {build_id}")
            return build_id
        except Exception as e:
            logger.error(f"Error extracting buildId: {e}")
            return None

    def fetch_api(self, category, slug, page=1, filters=None):
        endpoint = f"https://www.propertyfinder.ae/dataguru/_next/data/{self.build_id}/en/transactions/{category}/dubai/{slug}.json"
        
        # Build base params
        params = [
            ("category", category),
            ("page", str(page)),
            ("period", self.period),
            ("slug", "dubai"),
            ("slug", slug),
            ("fu", "0"),
            ("ob", "mr")
        ]
        
        if category == "rent":
            params.append(("rp", "y"))
            
        if filters:
            if "t" in filters:
                params.append(("t", str(filters["t"])))
            if "bdr[]" in filters:
                params.append(("bdr[]", str(filters["bdr[]"])))
            if "pf" in filters:
                params.append(("pf", str(filters["pf"])))
            if "pt" in filters:
                params.append(("pt", str(filters["pt"])))
            if "af" in filters:
                params.append(("af", str(filters["af"])))
            if "at" in filters:
                params.append(("at", str(filters["at"])))

        headers = {
            "x-nextjs-data": "1",
            "referer": f"https://www.propertyfinder.ae/en/transactions/{category}/dubai/{slug}",
            "accept": "*/*"
        }
        
        try:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{endpoint}?{query_string}"
            
            response = requests.get(full_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"_error": 404}
            else:
                logger.warning(f"API Error {response.status_code} for page {page}")
                return None
        except Exception as e:
            logger.error(f"Error fetching page {page} API: {e}")
            return None

    def parse_item(self, raw_transaction, category):

        unique_id = raw_transaction.get("id")
        contract_start_date = raw_transaction.get("contractStartDate")
        contract_end_date = raw_transaction.get("contractEndDate")
        property_size = raw_transaction.get("propertySize")
        bedrooms = raw_transaction.get("bedrooms")
        location = raw_transaction.get("locationName")
        price = raw_transaction.get("price")
        property_type = raw_transaction.get("propertyType")
        status = raw_transaction.get("status")
        transaction_date = raw_transaction.get("transactionDate")
        property_number = raw_transaction.get("propertyNumber")
        price_per_sqft = raw_transaction.get("pricePerSqft")
        
        item = {}
        item["unique_id"] = unique_id
        item["category"] = category
        item["contract_start_date"] = contract_start_date
        item["contract_end_date"] = contract_end_date
        item["property_size"] = str(property_size)
        item["bedrooms"] = str(bedrooms)
        item["location"] = location
        item["price"] = str(price)
        item["property_type"] = property_type
        item["status"] = status
        item["transaction_date"] = transaction_date
        item["property_number"] = property_number
        item["price_per_sqft"] = str(price_per_sqft)
        item["extraction_date"] = EXTRACTION_DATE
        
        try:
            transaction_item = TransactionItem(**item)
            transaction_item.validate()
            self.transactions_collection.insert_one(item)
        except pymongo.errors.DuplicateKeyError:
            pass
        except Exception as e:
            logger.error(f"Error saving transaction {item.get('unique_id')}: {e}")

    def slice_and_fetch(self, category, slug, filters, slice_queue, state_string=""):
        # Initial call to get count
        first_page_data = self.fetch_api(category, slug, page=1, filters=filters)
        if not first_page_data:
            return
            
        if first_page_data.get("_error") == 404:
            logger.debug(f"[{category.upper()}] {slug} {state_string} returned 404. Skipping.")
            return

        list_data = first_page_data.get("pageProps", {}).get("list", {})
        total_count = list_data.get("totalTransactionCount", 0)
        total_pages = list_data.get("totalPageCount", 1)
        transactions = list_data.get("transactionList", [])
        
        if total_count == 0:
            return
            
        if total_count > self.max_results_limit:
            # Slicing logic
            if not slice_queue:
                logger.warning(f"[{category.upper()}] {slug} {state_string} hit count {total_count} but no more slicers. Truncating to 500.")
                self.extract_pages(category, slug, filters, total_pages, first_transactions=transactions, state_string=state_string)
                return
                
            next_slice_axis = slice_queue[0]
            remaining_queue = slice_queue[1:]
            
            logger.info(f"[{category.upper()}] {slug} {state_string} count {total_count} > {self.max_results_limit}. Slicing by {next_slice_axis}.")
            
            if next_slice_axis == "type":
                for property_type in SLICER_PROPERTY_TYPES:
                    new_filters = dict(filters)
                    new_filters["t"] = property_type
                    self.slice_and_fetch(category, slug, new_filters, remaining_queue, f"{state_string}[type={property_type}]")
                    time.sleep(1)
            
            elif next_slice_axis == "bed":
                for bedroom_count in SLICER_BEDROOMS:
                    new_filters = dict(filters)
                    new_filters["bdr[]"] = bedroom_count
                    self.slice_and_fetch(category, slug, new_filters, remaining_queue, f"{state_string}[bed={bedroom_count}]")
                    time.sleep(1)
                    
            elif next_slice_axis == "price":
                prices = SLICER_PRICES
                ranges = [(0, prices[0])]
                for index in range(len(prices) - 1):
                    ranges.append((prices[index], prices[index+1]))
                ranges.append((prices[-1], None))
                
                for price_from, price_to in ranges:
                    new_filters = dict(filters)
                    if price_from > 0:
                        new_filters["pf"] = price_from
                    if price_to:
                        new_filters["pt"] = price_to
                    self.slice_and_fetch(category, slug, new_filters, remaining_queue, f"{state_string}[price={price_from}-{price_to}]")
                    time.sleep(1)
                    
            elif next_slice_axis == "area":
                areas = SLICER_AREAS
                ranges = [(0, areas[0])]
                for index in range(len(areas) - 1):
                    ranges.append((areas[index], areas[index+1]))
                ranges.append((areas[-1], None))
                
                for area_from, area_to in ranges:
                    new_filters = dict(filters)
                    if area_from > 0:
                        new_filters["af"] = area_from
                    if area_to:
                        new_filters["at"] = area_to
                    self.slice_and_fetch(category, slug, new_filters, remaining_queue, f"{state_string}[area={area_from}-{area_to}]")
                    time.sleep(1)
        else:
            # Good to extract directly
            logger.info(f"[{category.upper()}] {slug} {state_string} hit count {total_count}. Extracting directly.")
            self.extract_pages(category, slug, filters, total_pages, first_transactions=transactions, state_string=state_string)

    def extract_pages(self, category, slug, filters, total_pages, first_transactions=None, state_string=""):
        if first_transactions is None:
            first_transactions = []
            
        # Save first page
        for raw_transaction in first_transactions:
            self.parse_item(raw_transaction, category)
        
        if total_pages > 1:
            # Extract remaining pages up to 50
            max_pages = min(total_pages, 50)
            for page_number in range(2, max_pages + 1):
                page_data = self.fetch_api(category, slug, page=page_number, filters=filters)
                if not page_data or page_data.get("_error"):
                    break
                    
                list_data = page_data.get("pageProps", {}).get("list", {})
                transactions = list_data.get("transactionList", [])
                
                if not transactions:
                    break
                    
                for raw_transaction in transactions:
                    self.parse_item(raw_transaction, category)
                time.sleep(1.2)

    def start(self):
        if not self.build_id:
            return
            
        # Get locations from DB
        locations = list(LocationItem.objects.all().order_by("s"))
        logger.info(f"Found {len(locations)} locations to process.")
        
       
        for index, location in enumerate(locations, 1):
            slug = location.s
            if not slug:
                continue
                
            logger.info(f"Processing Location {index}/{len(locations)}: {slug}")
            
            # Rent
            slice_axes = ["type", "bed", "price", "area"]
            self.slice_and_fetch("rent", slug, filters={}, slice_queue=slice_axes)
            
            # Buy
            slice_axes = ["type", "bed", "price", "area"]
            self.slice_and_fetch("buy", slug, filters={}, slice_queue=slice_axes)

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connections closed")
        except:
            pass

if __name__ == "__main__":
    parser_obj = Parser()
    try:
        parser_obj.start()
    finally:
        parser_obj.close()
