
import requests
import logging
import urllib.parse
import time
import fastenal_settings as settings
import pymongo
from datetime import datetime
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FastenalCategoryScraper:
    def __init__(self):
        self.endpoint_url = settings.ENDPOINT_URL
        self.headers = settings.HEADERS
        self.cookies = settings.COOKIES

         #mongodb connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.DB_NAME
        self.collection_name = settings.COLLECTION_NAME
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MOngoDB : {e}")
            raise
        
        # Target root category
        self.root_category_id = settings.ROOT_CATEGORY_ID
        self.root_category_name = settings.ROOT_CATEGORY_NAME

    def fetch_categories(self, category_id, payload):
        #Fetches category data from the API for a given ID or payload.
        try:            
            # POST request
            response = requests.post(self.endpoint_url, headers=self.headers, cookies=self.cookies, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data.get("categoryList", [])
                elif isinstance(data, list):
                    return data
            else:
                logger.warning(f"Failed to fetch {category_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching {category_id}: {e}")
            return []
        return []

    def scrape(self):
        all_urls = []
        
        logger.info(f"Fetching Level 2 categories for {self.root_category_name}...")
        
        # Fetch Level 2 using product-search with specific payload
        l1_payload = {
            "attributeFilters": {},
            "categoryId": self.root_category_id,
            "categoryLevelOne": self.root_category_name,
            "pageUrl": f"/product/{urllib.parse.quote(self.root_category_name)}"
        }
        
        level2_nodes = self.fetch_categories(self.root_category_id, payload=l1_payload)
        
        if not level2_nodes:
            logger.warning("Could not find root category in response.")
            return []

        logger.info(f"Found {len(level2_nodes)} Level 2 categories.")

        # 2. Iterate Level 2 to get Level 3
        for l2 in level2_nodes:
            l2_name = l2.get("categoryLevelTwo") or l2.get("mp_categoryLabelTwo")
            l2_id = l2.get("categoryId")
            
            if l2_name and l2_id:
                logger.info(f"Processing L2: {l2_name} ({l2_id})")
                
                # Construct Rich Payload
                # "pageUrl": "/product/Adhesives%2C%20Sealants%2C%20and%20Tape/Tape",
                l1_enc = urllib.parse.quote(self.root_category_name)
                l2_enc = urllib.parse.quote(l2_name)
                page_url = f"/product/{l1_enc}/{l2_enc}"
                
                payload = {
                    "categoryId": l2_id,
                    "categoryLevelOne": self.root_category_name,
                    "categoryLevelTwo": l2_name,
                    "pageUrl": page_url,
                    "attributeFilters": {}
                }
                
                # Fetch Level 3
                level3_items = self.fetch_categories(l2_id, payload=payload)
                
                if level3_items:
                     logger.info(f"  > Found {len(level3_items)} L3 items.")
                else:
                     logger.info(f"  > No L3 items found.")
                
                for l3 in level3_items:
                    l3_name = l3.get("categoryLevelThree") or l3.get("mp_categoryLabelThree")
                    l3_id = l3.get("categoryId")
                    
                    if l3_name and l3_id:
                        l3_enc = urllib.parse.quote(l3_name)
                        
                        # Full URL
                        url = f"https://www.fastenal.com/product/{l1_enc}/{l2_enc}/{l3_enc}?categoryId={l3_id}"
                        all_urls.append(url)
                
                time.sleep(0.5)

        return all_urls

    #save urls to mongodb
    def save_to_db(self,urls):
            if not urls:
                logger.warning("No urls to save")
                return
            
            for url in urls:
                try:
                    result = self.collection.update_one(
                        {"url":url},
                        {
                            "$setOnInsert":{
                                "url":url,
                                "created_at":datetime.now()
                            }
                        },
                        upsert = True
                        )
                except Exception as e:
                    logger.error(f"Error saving URL {url}: {e}")
            logger.info(f"Database update Complete")

if __name__ == "__main__":
    scraper = FastenalCategoryScraper()
    urls = scraper.scrape()
  
    scraper.save_to_db(urls)
    if urls:
        print(f"Found {len(urls)} Deep URLs:")
        for u in urls:
            print(u)
    else:
        print("No Deep URLs found.")
    print(f"Count = {len(urls)}")