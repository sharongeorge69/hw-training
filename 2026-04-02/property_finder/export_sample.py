import csv
import logging
from pymongo import MongoClient
import sys
import os

# Add parent directory to path to allow absolute imports if run from inside property_finder dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME_FULLDUMP, EXPORT_LIMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CSV_HEADERS = [
  "unique_id",
  "category",
  "extraction_date",
  "contract_start_date",
  "contract_end_date",
  "property_size",
  "bedrooms",
  "location",
  "price",
  "property_type",
  "status",
  "transaction_date",
  "property_number",
  "price_per_sqft"
]

def format_number(val):
    try:
        # Check for explicitly stored "None" or similar
        if str(val).lower() == "none" or str(val).strip() == "":
            return ""
            
        f_val = float(val)
        if f_val == 0:
            return ""  # If 0, then ""
            
        return f"{f_val:.2f}"
    except (ValueError, TypeError):
        return ""

def export_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]
        
        logger.info(f"Connected to MongoDB. Exporting from {MONGO_COLLECTION_DATA}")
        
        cursor = collection.find({}).limit(EXPORT_LIMIT)
        total_docs = collection.count_documents({})
        export_count = min(total_docs, EXPORT_LIMIT)
        logger.info(f"Total documents available: {total_docs}. Exporting up to: {export_count}")
        
        with open(FILE_NAME_FULLDUMP, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, extrasaction='ignore', delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            count = 0
            for doc in cursor:
                row = {}
                for header in CSV_HEADERS:
                    val = doc.get(header, "")
                    
                    # Clean "None" -> ""
                    if val is None or str(val).strip() == "None":
                        val = ""
                    
                    val_str = str(val).strip()
                    
                    # Rounding and "0" checking
                    if header in ("price_per_sqft", "property_size"):
                        val_str = format_number(val_str)
                    
                    row[header] = val_str
                    
                writer.writerow(row)
                count += 1
                if count % 50 == 0:
                    logger.info(f"Exported {count}/{export_count} rows...")
                    
        logger.info(f"Successfully exported {count} rows to {FILE_NAME_FULLDUMP}")
        
    except Exception as e:
        logger.error(f"Error during export: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if 'client' in locals():
            client.close()

if __name__ == '__main__':
    export_data()
