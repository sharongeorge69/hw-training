import json
import re
import logging
from pymongo import MongoClient
import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Exporter:
    """
    Exporter for Moglix product data from MongoDB to JSON.
    Implements specific cleaning and transformation requirements.
    """
    def __init__(self):
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB
        self.collection_name = settings.MONGO_COLLECTION_DATA
        self.output_file = settings.FILE_NAME_FULLDUMP
        self.export_limit = settings.EXPORT_LIMIT
        
        self.headers = [
            "product_page_url",
            "product_name",
            "product_specifications",
            "product_description",
            "product_features",
            "product_image_url",
            "product_video_url"
        ]
        
        # MongoDB connection
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Connected to MongoDB. Exporting from '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def clean_text(self, text):
        """
        Applies cleaning rules:
        - Handle None/None string.
        - Replace specific entities: &a; -> &, &l;br&g; -> "", etc.
        - Normalize spaces and handle unicode escapes.
        """
        if text is None or str(text).strip().lower() == "none":
            return ""
        
        text = str(text)
        
        # Replace specific Moglix entities
        text = text.replace("&a;", "&")
        
        # Strip all &l;...&g; tags (Moglix's custom HTML entity format)
        text = re.sub(r'&l;.*?&g;', '', text)
        
        # General HTML entities handling (like &amp; if they exist)
        import html
        text = html.unescape(text)
        
        # Handle unicode escapes (e.g. \u00b3)
        try:
  
            text = text.encode('utf-8').decode('unicode_escape')
        except:
            pass
            
        # Clean extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def transform_specifications(self, specs_json):
        """
        Parses the specifications JSON and flattens single-item lists.
        Returns a dictionary for structured JSON export.
        """
        if not specs_json or str(specs_json).strip().lower() == "none":
            return {}
            
        try:
            specs = json.loads(specs_json) if isinstance(specs_json, str) else specs_json
            if not isinstance(specs, dict):
                return {}
            
            cleaned_specs = {}
            for key, value in specs.items():
                # Apply text cleaning to the key
                clean_key = self.clean_text(key)
                
                if isinstance(value, list):
                    # Flatten single-item lists
                    if len(value) == 1:
                        cleaned_specs[clean_key] = self.clean_text(value[0])
                    else:
                        # Clean each item in the list
                        cleaned_specs[clean_key] = [self.clean_text(v) for v in value]
                else:
                    cleaned_specs[clean_key] = self.clean_text(value)
            
            return cleaned_specs
        except Exception as e:
            logger.warning(f"Error transforming specifications: {e}")
            return {}

    def export(self):
        """Fetches data, applies cleaning, and writes to a JSON file with limit."""
        cursor = self.collection.find({}).limit(self.export_limit)
        total_docs = self.collection.count_documents({})
        actual_limit = min(total_docs, self.export_limit)
        logger.info(f"Exporting up to {actual_limit} documents to '{self.output_file}'...")
        
        try:
            all_data = []
            count = 0
            for doc in cursor:
                # Construct clean row
                row = {}
                for field in self.headers:
                    val = doc.get(field, "")
                    
                    if field == "product_specifications":
                        row[field] = self.transform_specifications(val)
                    else:
                        row[field] = self.clean_text(val)
                
                all_data.append(row)
                count += 1
                
                if count % 100 == 0:
                    logger.info(f"Processed {count}/{actual_limit} documents...")
            
            # Write to JSON file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Successfully exported {count} documents to {self.output_file}")
                
        except Exception as e:
            logger.error(f"Error during file writing: {e}")
            raise

    def close(self):
        self.client.close()
        logger.info("MongoDB connection closed.")

if __name__ == "__main__":
    exporter = Exporter()
    try:
        exporter.export()
    finally:
        exporter.close()
