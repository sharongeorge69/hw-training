import requests
import logging
from mongoengine import connect
from pymongo import MongoClient
import reelly_settings as settings
from reelly_items import ProductUrlItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReellyApiCrawler:
    def __init__(self):
        # MongoEngine connection for models
        connect(settings.MONGO_DB, host=settings.MONGO_URI)
        
        # PyMongo connection for direct insertion
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_URLS]
        
        logger.info(f"Connected to MongoDB: {settings.MONGO_DB}")

    def run(self):
        logger.info("Starting API-based project extraction...")
        params = {
            'limit': 2000
        }
        
        try:
            response = requests.get(settings.API_URL, params=params, headers=settings.HEADERS, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            projects = data.get('results', [])
            total_projects = data.get('count', 0)

            logger.info(f"Total projects: {total_projects}")
            
            total_saved = 0
            for project in projects:
                p_id = project.get('id')
                name = project.get('name')
                
                if p_id:
                    product_url = f"https://find.reelly.io/projects/{p_id}"
                    api_url = f"https://api-reelly.up.railway.app/api/internal/projects/{p_id}"
                    
                    item = {
                        "project_id": p_id,
                        "name": name,
                        "url": product_url,
                        "api_url": api_url
                    }
                    
                    try:
                        # Create instance and validate
                        product_item = ProductUrlItem(**item)
                        product_item.validate()
                        
                        self.collection.update_one(
                            {"project_id": item["project_id"]},
                            {"$set": item},
                            upsert=True
                        )
                        total_saved += 1
                    except Exception as e:
                        logger.error(f"Error saving URL for project {p_id}: {e}")
            
            logger.info(f"API Extraction complete. Total discovery saved: {total_saved}")

        except Exception as e:
            logger.error(f"API Crawler failed: {e}")

if __name__ == "__main__":
    crawler = ReellyApiCrawler()
    crawler.run()
