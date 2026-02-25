import requests
import json
import re
import logging
import html
import pymongo
from items import ProductItem
import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



class Parser:
    def __init__(self):
        self.headers = settings.HEADERS
        
        #mongodb connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB
        self.collection_name = settings.MONGO_COLLECTION_RESPONSE
        self.product_collection_name = settings.MONGO_COLLECTION_DATA
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.url_collection = self.db[self.collection_name]
            self.product_collection = self.db[self.product_collection_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")

    def start(self):
        try:
            logger.info(f"Started processing. Collection: {self.product_collection_name}")
            #checks total count of pdp urls
            total_docs = self.url_collection.count_documents({})
            logger.info(f"Total URLs: {total_docs}")
            
            for idx, doc in enumerate(self.url_collection.find(), 1):
                product_url = doc.get("product_url")
                if not product_url: continue

                if self.product_collection.find_one({"url": product_url}):
                    logger.debug(f"Skipped: {product_url}")
                    continue
                
                logger.info(f"Item {idx}/{total_docs}: {product_url}")
                try:
                    response = requests.get(product_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    if response:
                        self.parse_item(product_url, response)
                except Exception as e:
                    logger.error(f"Request error for {product_url}: {e}")
                
        except Exception as e:
            logger.error(f"Batch error: {e}")
    #parse item
    def parse_item(self, url, response):
        try:
            match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.+?});', response.text)
            if not match:
                logger.warning(f"No PRELOADED_STATE for {url}")
                return

            data = json.loads(match.group(1).replace("undefined", "null"))
            pd = data.get('productDetails', {})
            lots = pd.get('lots', [])
            
            # Brand & Description
            brand_data = pd.get('brand')
            brand = brand_data.get('name') if isinstance(brand_data, dict) else brand_data
            
            description = ""
            fit = ""
            colors = []
            sizes = set()

            if lots:
                lot = lots[0]
                raw_desc = lot.get('description', '')
                description = html.unescape(re.sub(r'<[^>]+>', '', raw_desc)).strip() if raw_desc else ""
                
                for attr in lot.get('bulletedAttributes', []):
                    desc = attr.get('description', '')
                    if desc.lower().startswith("fit:"):
                        fit = desc.split(':', 1)[1].strip()
                        break

                color_seq = pd.get('colorSequences') or lot.get('colorSequences', [])
                colors = [cs['color'] for cs in color_seq if 'color' in cs]

                for item in lot.get('items', []):
                    for ov in item.get('optionValues', []):
                        if ov.get('name', '').lower() == 'size' and ov.get('value'):
                            sizes.add(ov.get('value').title())
                    if item.get('size'):
                        sizes.add(item.get('size').title())

            if not description and pd.get('description'):
                description = html.unescape(re.sub(r'<[^>]+>', '', pd.get('description'))).strip()

            # Images & Valuation
            images = [img['url'] for img in pd.get('images', []) if isinstance(img, dict) and 'url' in img]
            valuation = pd.get('valuation', {})
            rating = valuation.get('rating')
            reviews = valuation.get('reviews', {}).get('count', 0) if valuation.get('reviews') else 0

            # Pricing API
            selling_price, regular_price, discount = None, None, ""
            if pd.get('id'):
                price_url = f"https://browse-api.jcpenney.com/v2/product-aggregator/{pd.get('id')}/additional-details?deliveryAvailabilityCheckRequired=false&GPA=false"
                try:
                    api_headers = {**self.headers, 'Accept': 'application/json'}
                    price_resp = requests.get(price_url, headers=api_headers, timeout=5)
                    if price_resp.status_code == 200:
                        price_data = price_resp.json()
                        lot_price = price_data.get('lotPrice', {})
                        data_list = lot_price.get('data', [])
                        if data_list:
                            for amt in data_list[0].get('amounts', []):
                                if amt.get('minPercentOff'):
                                    discount = amt.get('minPercentOff')
                                if amt.get('type') == 'ORIGINAL':
                                    regular_price = amt.get('max')
                                elif amt.get('type') in ['SALE', 'CLEARANCE']:
                                    selling_price = amt.get('max')
                except Exception as e:
                    logger.error(f"Pricing error for {pd.get('id')}: {e}")

            if not selling_price and regular_price:
                selling_price = regular_price

            # ITEM YIELD
            item = {
                "unique_id": str(pd.get('id', "")),
                "url": str(url),
                "productname": str(pd.get('name', "")),
                "brand": str(brand) if brand else "",
                "selling_price": float(selling_price) if selling_price is not None and selling_price != "" else "",
                "regular_price": float(regular_price) if regular_price is not None and regular_price != "" else "",
                "discount": str(discount) if discount else "",
                "description": str(description),
                "specification": "",
                "fit_type": str(fit),
                "image": ", ".join(images),
                "rating": str(rating) if rating else "",
                "review": str(reviews),
                "size": ", ".join(sorted(list(sizes))),
                "colour": ", ".join(colors)
            }
            try:
                product_item = ProductItem(**item)
                product_item.validate()
                self.product_collection.insert_one(item)
            except Exception as e:
                logger.error(f"Save error: {e}")
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")

    def close(self):
        #close connection
        try:
            self.client.close()
        except:
            pass

if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()
