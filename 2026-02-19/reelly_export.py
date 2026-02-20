import csv
import logging
from pymongo import MongoClient
import reelly_settings as settings

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def export_to_csv():
    """
    Exports data from reelly_products collection to a CSV file.
    """
    try:
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB]
        collection = db[settings.MONGO_COLLECTION_PRODUCTS]
        
        # Get all records
        cursor = collection.find({}, {'_id': 0}) # Exclude MongoDB ID
        data = list(cursor)
        
        if not data:
            logger.warning("No data found in collection to export.")
            return

        # Define explicit fieldnames to ensure order and completeness
        fieldnames = [
            "project_id", "name", "url", "developer_name", "main_office",
            "construction_start_date", "construction_end_date", "price_from",
            "district", "floors", "amenities", "description",
            "furnishing", "service_charge", "resale_conditions", "unit_types",
            "cover_image_url"
        ]
        
        file_path = f"/home/sharon/Documents/scraping_practice/reelly/{settings.FILE_NAME_FULLDUMP}"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
                
        logger.info(f"Successfully exported {len(data)} records to {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Export failed: {e}")
        return None

if __name__ == "__main__":
    export_to_csv()
