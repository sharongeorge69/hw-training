import json
import re
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA

def clean_data(data):
    if isinstance(data, list):
        return [clean_data(x) for x in data]
    elif isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif data is None:
        return ""
    elif isinstance(data, str):
        # Remove HTML tags and replace with space
        clean_text = re.sub(r'<[^>]*>', ' ', data)
        # Remove extra spaces and strip
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    else:
        return data

def export_data():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]
        
        projection = {
            "_id": 0,
            "inspection_details": 1,
            "developer_details": 1,
            "management_companies": 1,
            "escrow_account": 1
        }
        
        raw_data = list(collection.find({}, projection).limit(200))
        
        # Clean data (replace nulls, remove HTML, normalize spaces)
        data = clean_data(raw_data)
        
        # Save to JSON file
        output_file = "dubailand_export.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully exported {len(data)} records to {output_file}")
        
        client.close()
        
    except Exception as e:
        print(f"Error during export: {e}")

if __name__ == "__main__":
    export_data()
