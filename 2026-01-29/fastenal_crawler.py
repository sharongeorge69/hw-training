import requests
import logging
import urllib.parse
import time
import pymongo
import fastenal_settings as settings
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FastenalPDPCrawler:
    def __init__(self):
        self.endpoint_url = settings.ENDPOINT_URL
        self.headers = settings.HEADERS
        self.cookies = settings.COOKIES
        
        # MongoDB connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.DB_NAME
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.category_collection = self.db[settings.CATEGORY_COLLECTION_NAME]
            self.product_collection = self.db[settings.PRODUCT_COLLECTION_NAME]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
     
    # Parse Category URL to extract payload components
    def parse_category_url(self, url):
        parsed = urllib.parse.urlparse(url)
        path_segments = parsed.path.strip("/").split("/")
        
        if len(path_segments) < 4:
            logger.warning(f"Unexpected URL structure: {url}")
            return None

        # Decode segments
        # Example: https://www.fastenal.com/product/Adhesives%2C%20Sealants%2C%20and%20Tape/Tape/Packaging%20Tape?categoryId=602009
        # path_segments = ['product', 'Adhesives, Sealants, and Tape', 'Tape', 'Packaging Tape']
        l1 = urllib.parse.unquote(path_segments[1])
        l2 = urllib.parse.unquote(path_segments[2])
        l3 = urllib.parse.unquote(path_segments[3])
        
        # Extract Category ID
        query_params = urllib.parse.parse_qs(parsed.query)
        category_id = query_params.get('categoryId', [None])[0]
        
        if not category_id:
            logger.warning(f"No categoryId found in URL: {url}")
            return None
            
        return {
            "categoryId": category_id,
            "categoryLevelOne": l1,
            "categoryLevelTwo": l2,
            "categoryLevelThree": l3,
            "pageUrl": parsed.path
        }
    # Fetch products from the API
    def fetch_products(self, context, page=1):
        payload = {
            "attributeFilters": {},
            "categoryId": context["categoryId"],
            "categoryLevelOne": context["categoryLevelOne"],
            "categoryLevelTwo": context["categoryLevelTwo"],
            "categoryLevelThree": context["categoryLevelThree"],
            "pageUrl": context["pageUrl"],
            "page": page
        }
        
        try:
            response = requests.post(self.endpoint_url, headers=self.headers, cookies=self.cookies, json=payload)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                     return data.get("productList", [])
            else:
                logger.warning(f"Failed to fetch page {page} for {context['categoryId']}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            return []
        return []

    def save_product_url(self, product, category_level_three=None):
        #Saves a product URL to MongoDB.
        try:
             # Construct PDP URL using SKU
             sku = product.get("sku")
             if sku:
                  product_url = f"https://www.fastenal.com/product/details/{sku}"
             else:
                  product_url = None

             if product_url:
                self.product_collection.update_one(
                    {"url": product_url},
                    {
                        "$setOnInsert": {
                            "url": product_url,
                            "sku": sku,
                            "created_at": datetime.now(),
                            "pageUrl": f"/product/details/{sku}",
                            "categoryLevelThree": category_level_three
                        }
                    },
                    upsert=True
                )
        except Exception as e:
            logger.error(f"Error saving product: {e}")

    def crawl(self):
        # 1. Get all category URLs
        categories = list(self.category_collection.find({}, {"url": 1}))
        logger.info(f"Found {len(categories)} categories to crawl.")
        
        for cat_doc in categories:
            url = cat_doc.get("url")
            if not url: continue
            
            logger.info(f"Processing Category: {url}")
            
            # 2. Parse Context - Data needed for payload
            context = self.parse_category_url(url)
            if not context: continue
            
            # 3. Pagination Loop
            page = 1
            while True:
                logger.info(f"  Fetching Page {page}...")
                products = self.fetch_products(context, page=page)
                
                if not products:
                    logger.info("  No more products found.")
                    break
                
                logger.info(f"  Found {len(products)} products.")
                
                # 4. Save Products
                for p in products:
                    self.save_product_url(p, context.get("categoryLevelThree"))
                
                page += 1
                time.sleep(0.5) # Politeness

if __name__ == "__main__":
    crawler = FastenalPDPCrawler()
    crawler.crawl()
