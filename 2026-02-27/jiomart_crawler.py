from curl_cffi import requests
import logging
from settings import headers_crawler, json_data_crawler, CRAWLER_URL, MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, cookies_crawler
import pymongo
from items import ProductUrlItem
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.url = CRAWLER_URL
        self.headers = headers_crawler
        self.payload = json_data_crawler
        self.cookies = cookies_crawler
        
        # mongodb connection
        self.mongo_uri = MONGO_URI
        self.db_name = MONGO_DB
        self.collection_name = MONGO_COLLECTION_RESPONSE
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.collection.create_index("unique_id", unique=True)
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")


    def start(self):
        next_page_token = self.payload.get('pageToken', "")
        page_count = 1
        
        while True:
            try:
                payload = self.payload
                # Update payload with next page token if it exists
                if next_page_token:
                    payload['pageToken'] = next_page_token
                
                response = requests.post(self.url, headers=self.headers, json=payload, timeout=20, impersonate="chrome110", cookies=self.cookies)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch page {page_count}: Status {response.status_code}")
                    break

                data = response.json()
                if not self.parse_item(data):
                    break

                next_page_token = data.get("nextPageToken")
                logger.info(f"Page {page_count} processed")
                
                if not next_page_token:
                    logger.info("End of pagination")
                    break
                
                page_count += 1
            except Exception as e:
                logger.error(f"Pagination error at page {page_count}: {e}")
                break

    def parse_item(self, data):
        results = data.get("results", [])
        if not results:
            return False
        
        for r in results:
            product_data = r.get("product", {})
            variants = product_data.get("variants", [])
            
            if not variants:
                continue
                
            variant = variants[0]
            product_url = variant.get("uri")

            match = re.search(r'(\d+)(?=[^/]*$)', product_url)
            unique_id = match.group(1) if match else None
            if not product_url:
                continue
            
            product_name = product_data.get("title")
            
            # brand
            brand = ""
            if variant.get("brands"):
                brand = variant.get("brands")[0]
            
            attributes = variant.get("attributes", {})
            #selling price
            selling_price = None
            avg_price_list = attributes.get("avg_selling_price", {}).get("numbers", [])
            if avg_price_list:
                selling_price = str(avg_price_list[0])
            
            # Discount percentage
            percentage_discount = None
            avg_discount_list = attributes.get("avg_discount_pct", {}).get("numbers", [])
            if avg_discount_list:
                percentage_discount = str(avg_discount_list[0])
                
            # Seller names
            seller_name = None
            seller_list = attributes.get("seller_names", {}).get("text", [])
            if seller_list:
                seller_name = seller_list[0]
                
            # Image URL
            image_url = None
            images = variant.get("images", [])
            if images:
                image_url = images[0].get("uri")
            
            item_data = {
                "unique_id": unique_id,
                "pdp_url": product_url,
                "product_name": product_name,
                "brand": brand,
                "selling_price": selling_price,
                "percentage_discount": percentage_discount,
                "image_url": image_url,
                "seller_name": seller_name
            }

            try:
                # Validation
                product_url_item = ProductUrlItem(**item_data)
                product_url_item.validate()

                self.collection.insert_one(item_data)
                logger.info(f"Saved: {product_url}")
            except pymongo.errors.DuplicateKeyError:
                continue
            except Exception as e:
                logger.error(f"Save error for {product_url}: {e}")
                
        return True

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    crawler_obj = Crawler()
    crawler_obj.start()
    crawler_obj.close()
