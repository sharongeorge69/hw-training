import style_union_settings as settings
import requests
from parsel import Selector
import logging
import pymongo
from datetime import datetime
import time
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StyleUnionParser:
    def __init__(self):
        self.headers = settings.HEADERS
        
        # MongoDB connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.DB_NAME
        self.product_urls_collection_name = settings.COLLECTION_PRODUCT_URLS
        self.products_collection_name = settings.COLLECTION_PRODUCTS
        
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.url_collection = self.db[self.product_urls_collection_name]
            self.product_collection = self.db[self.products_collection_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_pending_urls(self):
        # Fetch URLs that haven't been parsed yet
        try:
            cursor = self.url_collection.find({}, {"url": 1})
            urls = [doc['url'] for doc in cursor]
            
            processed_urls = self.product_collection.distinct("product_url")
            pending = list(set(urls) - set(processed_urls))
            
            logger.info(f"Found {len(pending)} pending URLs to parse")
            return pending
        except Exception as e:
            logger.error(f"Error fetching pending URLs: {e}")
            return []

    def extract_text(self, sel, xpaths):
        # Helper to extract text from XPaths
        if isinstance(xpaths, str):
            xpaths = [xpaths]
        
        for xpath in xpaths:
            try:
                nodes = sel.xpath(xpath)
                if not nodes:
                    continue
                    
                first = nodes[0]
                extracted = first.get()
                
                # If element, extract text content recursively
                if '<' in extracted and '>' in extracted: 
                    text_val = first.xpath('string(.)').get()
                    if text_val:
                        return text_val.strip()
                else:
                    # Text node
                    if extracted:
                         return extracted.strip()

            except Exception:
                continue
                
        return ""

    def parse_product(self, url):
        retries = settings.RETRY_COUNT
        delay = settings.INITIAL_DELAY
        
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=settings.TIMEOUT)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limited on {url}. Waiting {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                
                response.raise_for_status()
                
                sel = Selector(text=response.text)
                data = {}
                data['product_url'] = url
                
                # Static fields
                data['brand'] = "Style Union"
                data['country_of_origin'] = "India"
                
                # 1. Title
                data['title'] = self.extract_text(sel, "//h1[contains(@class,'product__title')]")

                # 2. Breadcrumbs
                breadcrumbs_list = sel.xpath("//nav[@aria-label='breadcrumbs']//li[contains(@class, 'breadcrumbs__item')]//a[normalize-space(text())]/text()").getall()
                if breadcrumbs_list:
                    data['breadcrumbs'] = " > ".join([b.strip() for b in breadcrumbs_list if b.strip()])
                else:
                     data['breadcrumbs'] = ""

                # 3. Regular & Selling Price
                price_xpaths = ["//span[contains(@class,'regular-price')]", 
                                "//div[contains(@class,'price__regular')]//span"]
                data['regular_price'] = self.extract_text(sel, price_xpaths)
                data['selling_price'] = self.extract_text(sel, price_xpaths)

                # 4. SKU
                raw_sku = self.extract_text(sel, ["//p[contains(@class,'product__sku')]//b", "//p[contains(@id,'sku-')]//b"])
                data['sku'] = raw_sku.replace("SKU:", "").strip()
                
                # 5. Description
                data['description'] = self.extract_text(sel, "//div[contains(@class,'accordion__content')]//div[contains(@class,'desc_inner')][2]//div[@class='acc__panel']")
                
                # 6. Dimensions
                dim_nodes = sel.xpath("//div[contains(@class, 'form__variants')]//span[@class='color__swatch-name']")
                if dim_nodes:
                    dims = [node.xpath('string(.)').get().strip() for node in dim_nodes]
                    data['dimensions'] = ", ".join([d for d in dims if d])
                else:
                    data['dimensions'] = ""

                # 7. Net Quantity
                net_qty = sel.xpath("//input[contains(@class,'quantity__input')]/@value").get()
                data['net_quantity'] = net_qty if net_qty else "1"

                # 8. Fit
                data['fit'] = self.extract_text(sel, ["//strong[contains(text(),'Fit')]/following-sibling::text()",
                                                  "//b[contains(text(),'Fit')]/following-sibling::text()"])

                # 9. Care Instruction
                data['care_instruction'] = self.extract_text(sel, "//h3[text()='Wash and Care']/following::div[@class='acc__panel'][1]")

                # 10. Fabric Composition
                data['fabric_composition'] = self.extract_text(sel, ["//strong[contains(text(),'Fabric')]/following-sibling::text()",
                                                                 "//b[contains(text(),'Fabric')]/following-sibling::text()"])
                
                data['timestamp'] = datetime.now()
                return data

            except requests.RequestException as e:
                logger.error(f"Request failed for {url}: {e}")
                time.sleep(2)
        
        return None

    def save_product(self, data):
        if not data:
            return
        
        try:
            self.product_collection.update_one(
                {"product_url": data['product_url']},
                {"$set": data},
                upsert=True
            )
            logger.info(f"Saved {data.get('sku')} - {data['product_url']}")
        except Exception as e:
            logger.error(f"Error saving product: {e}")

    def run(self):
        urls = self.get_pending_urls()
        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}: {url}")
            data = self.parse_product(url)
            if data:
                self.save_product(data)
            
            # Politeness delay
            sleep_time = random.uniform(2, 4)
            time.sleep(sleep_time)

if __name__ == "__main__":
    parser = StyleUnionParser()
    parser.run()
