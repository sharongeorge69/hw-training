import requests
import math
import logging
import settings
from urllib.parse import urljoin
import pymongo
from items import ProductUrlItem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.headers = settings.HEADERS
        
        #mongodb connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB
        self.collection_name = settings.MONGO_COLLECTION_CATEGORY
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
    #start
    def start(self):
        try:
            categories = list(self.collection.find({"api_url": {"$exists": True}}))
            logger.info(f"Processing {len(categories)} categories")
            for cat in categories:
                try:
                    url = cat.get('api_url')
                    response = requests.get(url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        self.parse_item(response, cat)
                except Exception as e:
                    logger.error(f"Error in {cat.get('url')}: {e}")
        except Exception as e:
            logger.error(f"Start error: {e}")

    #parse item
    def parse_item(self, response, meta):
        try:
            cat_url = meta.get('url')
            cat_name = meta.get('subcategory_name')
            data = response.json()
            total = data.get("organicZoneInfo", {}).get("totalNumRecs", 0)
            logger.info(f"  Category: {cat_url} - Total records: {total}")
            
            facets = data.get("facets", [])
            if not isinstance(facets, list):
                facets = facets.get("facetList", [])
                
            priority_facets = ["Price Range", "Style", "Brand", "Stone"]
            found_facets = False
            
            # Check for priority facets to handle large categories via buckets
            for f_name in priority_facets:
                target = next((f for f in facets if f.get("facetName") == f_name), None)
                if target:
                    found_facets = True
                    logger.info(f"  Using facet: {f_name}")
                    for bucket in target.get("facetValueList", []):
                        if not bucket.get("count") or not bucket.get("apiUrl"): continue
                        
                        b_url = "https://search-api.jcpenney.com" + bucket["apiUrl"]
                        logger.info(f"    Bucket: {bucket['name']} ({bucket['count']})")
                        self.crawl_pagination(b_url, cat_url, bucket['count'], cat_name)
                    break 
            
            if not found_facets:
                 self.crawl_pagination(meta.get('api_url'), cat_url, total, cat_name)
        except Exception as e:
            logger.error(f"Parse error for {meta.get('url')}: {e}")
  
    #pagination
    def crawl_pagination(self, api_url, cat_url, total, cat_name):
        pages = math.ceil(total / 48) if total else 1
        for page in range(1, pages + 1):
            try:
                sep = "&" if "?" in api_url else "?"
                url = f"{api_url}{sep}page={page}"
                if "productGridView=" not in url: url += "&productGridView=medium"
                
                resp = requests.get(url, headers=self.headers, timeout=15)
                if resp.status_code != 200: continue
                
                if page == 1 and not total:
                    total = resp.json().get("organicZoneInfo", {}).get("totalNumRecs", 0)
                    pages = math.ceil(total / 48)

                if not self.save_products(resp, cat_url, cat_name): break
                logger.info(f"    Page {page}/{pages} done")
            except Exception as e:
                logger.error(f"    Page {page} error: {e}")

    def save_products(self, resp, cat_url, cat_name):
        #Extract and save products from page response
        products = resp.json().get("organicZoneInfo", {}).get("products", [])
        if not products: return False
        
        for p in products:
            suffix = p.get("pdpUrl")
            if not suffix: continue
            
            p_url = urljoin("https://www.jcpenney.com", suffix)
            cat_obj = {"url": cat_url, "name": cat_name}
            
            item_data = {
                "product_url": p_url,
                "name": p.get('name'),
                "categories": [cat_obj]
            }

            try:
                # Validation using ProductUrlItem
                product_url_item = ProductUrlItem(**item_data)
                product_url_item.validate()

                self.db[settings.MONGO_COLLECTION_RESPONSE].insert_one(item_data)
            except Exception as e:
                logger.error(f"Save error for {p_url}: {e}")
        return True

    def close(self):
        """connection close"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    crawler_obj = Crawler()
    crawler_obj.start()
    crawler_obj.close()
