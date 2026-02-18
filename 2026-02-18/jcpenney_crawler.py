import requests
import math
import logging
import jcpenney_settings as settings
from urllib.parse import urljoin
from mongoengine import connect, DynamicDocument, StringField
from jcpenney_items import ProductUrlItem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CategoryDoc(DynamicDocument):
    meta = {'collection': settings.MONGO_COLLECTION_CATEGORY}

class Crawler:
    def __init__(self):
        connect(settings.MONGO_DB, host=settings.MONGO_URI)
        self.headers = settings.HEADERS
        logger.info("Connected to MongoDB via MongoEngine")

    def start(self):
        categories = CategoryDoc.objects(api_url__exists=True)
        logger.info(f"Processing {len(categories)} categories")
        for cat in categories:
            try:
                self.process_category(cat)
            except Exception as e:
                logger.error(f"Error in {cat.url}: {e}")

    def process_category(self, cat):
        logger.info(f"Category: {cat.url}")
        try:
            resp = requests.get(cat.api_url, headers=self.headers, timeout=15)
            if resp.status_code != 200: return

            data = resp.json()
            total = data.get("organicZoneInfo", {}).get("totalNumRecs", 0)
            logger.info(f"  Total records: {total}")
            
            facets = data.get("facets", [])
            if not isinstance(facets, list):
                facets = facets.get("facetList", [])
                
            priority_facets = ["Price Range", "Item Type", "Brand"]
            found_facets = False
            
            for f_name in priority_facets:
                target = next((f for f in facets if f.get("facetName") == f_name), None)
                if target:
                    found_facets = True
                    logger.info(f"  Using facet: {f_name}")
                    for bucket in target.get("facetValueList", []):
                        if not bucket.get("count") or not bucket.get("apiUrl"): continue
                        
                        b_url = "https://search-api.jcpenney.com" + bucket["apiUrl"]
                        logger.info(f"    Bucket: {bucket['name']} ({bucket['count']})")
                        self.crawl_pagination(b_url, cat.url, bucket['count'], cat.subcategory_name)
                    break # Stop at first priority facet found
            
            if not found_facets:
                 self.crawl_pagination(cat.api_url, cat.url, total, cat.subcategory_name)
        except Exception as e:
            logger.error(f"Failed category {cat.url}: {e}")

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
        products = resp.json().get("organicZoneInfo", {}).get("products", [])
        if not products: return False
        
        for p in products:
            suffix = p.get("pdpUrl")
            if not suffix: continue
            
            p_url = urljoin("https://www.jcpenney.com", suffix)
            cat_obj = {"url": cat_url, "name": cat_name}
            
            # Use MongoEngine for atomic update (addToSet for categories)
            ProductUrlItem.objects(product_url=p_url).update_one(
                set__name=p.get('name'),
                add_to_set__categories=cat_obj,
                upsert=True
            )
        return True

if __name__ == "__main__":
    Crawler().start()
