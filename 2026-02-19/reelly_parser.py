import requests
import logging
import re
import time
from pymongo import MongoClient
import reelly_settings as settings
# import reelly_items

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReellyParser:
    def __init__(self):
        # PyMongo connection for direct insertion
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_DATA]
        self.url_collection = self.db[settings.MONGO_COLLECTION_RESPONSE]
        
        logger.info(f"Connected to MongoDB: {settings.MONGO_DB}")
        self.detail_base_url = "https://api-reelly.up.railway.app/api/internal/projects/"

    def fetch_project_details(self, project_id):
        url = f"{self.detail_base_url}{project_id}"
        try:
            response = requests.get(url, headers=settings.HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch details for project {project_id}: {e}")
            return None

    def sanitize(self, value):
        #Replaces None with empty string.
        return value if value is not None else ""

    def clean_description(self, text):
        #Removes markdown headers (####), newlines, and extra whitespace.
        if not text:
            return ""
        # Remove literal \n and \r
        text = text.replace('\\n', ' ').replace('\\r', ' ')
        # Remove markdown headers like #####
        text = re.sub(r'#+\s*', '', text)
        # Split by lines (handles \n, \r, \r\n, etc.) and join with space
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = " ".join(lines)
        return cleaned

    def parse_item(self, data):
        p_id = data.get('id')
        if not p_id:
            return None

        # Extract nested developer 
        dev = data.get('developer') or {}
        dev_name = self.sanitize(dev.get('name'))
        
        main_office = dev.get('main_office') or {}
        main_office_addr = self.sanitize(main_office.get('address'))

        # Extract amenities list and convert to comma-separated string
        amenities_raw = data.get('amenities') or []
        amenities_list = [a.get('amenity', {}).get('name') for a in amenities_raw if a.get('amenity', {}).get('name')]
        amenities_str = ", ".join(amenities_list)

        # Extract cover image
        cover_image = data.get('cover_image') or {}
        cover_image_url = self.sanitize(cover_image.get('url'))

        # Build item dictionary matching ProductItem schema
        item = {
            "project_id": p_id,
            "name": self.sanitize(data.get('name')),
            "construction_start_date": self.sanitize(data.get('construction_start_date')),
            "construction_end_date": self.sanitize(data.get('construction_end_date')),
            "developer_name": dev_name,
            "main_office": main_office_addr,
            "description": self.clean_description(data.get('overview')),
            "amenities": amenities_str,
            "furnishing": self.sanitize(data.get('furnishing')),
            "service_charge": self.sanitize(data.get('service_charge')),
            "resale_conditions": self.sanitize(data.get('resale_conditions')),
            "unit_types": self.sanitize(data.get('unit_types')),
            "price_from": float(data.get('min_price')) if data.get('min_price') is not None else 0,
            "district": self.sanitize(data.get('district')),
            "cover_image_url": cover_image_url,
            "floors": self.sanitize(data.get('floors')),
            "url": f"https://find.reelly.io/projects/{p_id}"
        }
        try:
            # Create instance and validate
            # product_item = reelly_items.ProductItem(**item)
            # product_item.validate()
            
            self.collection.insert_one(item)
        except Exception as e:
            logger.error(f"Error saving project {item.get('project_id')}: {e}")

    def start(self):
        # Get all discovered project IDs via PyMongo
        total = self.url_collection.count_documents({"project_id": {"$exists": True}})
        project_urls = self.url_collection.find({"project_id": {"$exists": True}})
        logger.info(f"Found {total} project IDs to parse.")

        count = 0
        for p_url in project_urls:
            p_id = p_url.get("project_id")
            if not p_id:
                continue
            count += 1
            
            logger.info(f"Progress: {count}/{total} projects parsed (Project ID: {p_id})...")

            data = self.fetch_project_details(p_id)
            if data:
                self.parse_item(data)
            
            time.sleep(0.1)

        logger.info("Parsing complete.")

    def close(self):
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
                logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

if __name__ == "__main__":
    parser = ReellyParser()
    parser.start()
    parser.close()
