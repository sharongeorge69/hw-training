import logging
import time
import requests
from pymongo import MongoClient
import pymongo

# Local imports
from settings import HEADERS, PARAMS, MONGO_URI, MONGO_DB, MONGO_COLLECTION_LOCATIONS, EXTRACTION_DATE
from items import LocationItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.headers = HEADERS
        self.params = PARAMS
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.location_collection = self.db[MONGO_COLLECTION_LOCATIONS]
        
        # Create unique index to avoid duplicates
        self.location_collection.create_index("s", unique=True)
        logger.info("Connected to MongoDB") 

    def parse_item(self, response_data, url):
        if not response_data:
            logger.error(f"Received empty response data for {url}")
            return False

        try:
            if isinstance(response_data, list):
                locations = response_data
            elif isinstance(response_data, dict) and "outputs" in response_data and "location-list" in response_data["outputs"]:
                locations = response_data["outputs"]["location-list"]
            else:
                logger.warning(f"Unexpected API response format for {url}. Type: {type(response_data)}")
                return False

            if not locations:
                logger.warning(f"No locations to save from {url}.")
                return False

            saved_count = 0
            duplicate_count = 0
            
            for loc in locations:
                item_data = {
                    "n": loc.get("n"),
                    "l_t": loc.get("l_t"),
                    "s": loc.get("s"),
                    "en_s": loc.get("en_s"),
                    "extraction_date": EXTRACTION_DATE
                }
                
                try:
                    location_item = LocationItem(**item_data)
                    location_item.validate()
                    self.location_collection.insert_one(item_data)
                    saved_count += 1
                except pymongo.errors.DuplicateKeyError:
                    duplicate_count += 1
                except Exception as e:
                    logger.error(f"  Error saving location {item_data.get('s')}: {e}")
            
            logger.info(f"Locations Processed: Total={len(locations)}, New Saved={saved_count}, Duplicates={duplicate_count}")
            return True

        except Exception as e:
            logger.error(f"Error parsing items from {url}: {e}")
            return False

    def start(self):
        url = 'https://www.propertyfinder.ae/api/pwa/location/list'
        max_retries = 3
        logger.info(f"Starting crawler for {url}...")
        
        success = False
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=self.params, headers=self.headers, timeout=15)
                
                if response.status_code == 200:
                    if self.parse_item(response.json(), url):
                        success = True
                        break
                    else:
                        logger.error(f"  Parsing failed for {url} on attempt {attempt + 1}")
                else:
                    logger.warning(f"  Attempt {attempt + 1} failed for {url} with status code {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"  Attempt {attempt + 1} failed for {url} with error: {e}")
            
            # Exponential backoff on retry 
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        if not success:
            logger.error(f"Failed to crawl {url} after {max_retries} attempts")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    crawler_obj = Crawler()
    try:
        crawler_obj.start()
    finally:
        crawler_obj.close()
