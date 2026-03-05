import csv
import logging
import re
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME_FULLDUMP

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

csv_headers = [
  "unique_id",
  "competitor_name",
  "store_name",
  "store_addressline1",
  "store_addressline2",
  "store_suburb",
  "store_state",
  "store_postcode",
  "store_addressid",
  "extraction_date",
  "product_name",
  "brand",
  "brand_type",
  "grammage_quantity",
  "grammage_unit",
  "drained_weight",
  "producthierarchy_level1",
  "producthierarchy_level2",
  "producthierarchy_level3",
  "producthierarchy_level4",
  "producthierarchy_level5",
  "producthierarchy_level6",
  "producthierarchy_level7",
  "regular_price",
  "selling_price",
  "price_was",
  "promotion_price",
  "promotion_valid_from",
  "promotion_valid_upto",
  "promotion_type",
  "percentage_discount",
  "promotion_description",
  "package_sizeof_sellingprice",
  "per_unit_sizedescription",
  "price_valid_from",
  "price_per_unit",
  "multi_buy_item_count",
  "multi_buy_items_price_total",
  "currency",
  "breadcrumb",
  "pdp_url",
  "variants",
  "product_description",
  "instructions",
  "storage_instructions",
  "preparationinstructions",
  "instructionforuse",
  "country_of_origin",
  "allergens",
  "age_of_the_product",
  "age_recommendations",
  "flavour",
  "nutritions",
  "nutritional_information",
  "vitamins",
  "labelling",
  "grade",
  "region",
  "packaging",
  "receipies",
  "processed_food",
  "barcode",
  "frozen",
  "chilled",
  "organictype",
  "cooking_part",
  "handmade",
  "max_heating_temperature",
  "special_information",
  "label_information",
  "dimensions",
  "special_nutrition_purpose",
  "feeding_recommendation",
  "warranty",
  "color",
  "model_number",
  "material",
  "usp",
  "dosage_recommendation",
  "tasting_note",
  "food_preservation",
  "size",
  "rating",
  "review",
  "file_name_1",
  "image_url_1",
  "file_name_2",
  "image_url_2",
  "file_name_3",
  "image_url_3",
  "file_name_4",
  "image_url_4",  
  "file_name_5",
  "image_url_5",
  "file_name_6",  
  "image_url_6",
  "competitor_product_key",
  "fit_guide",
  "occasion",
  "material_composition",
  "style",
  "care_instructions",
  "heel_type",
  "heel_height",
  "upc",
  "features",
  "dietary_lifestyle",
  "manufacturer_address",
  "importer_address",
  "distributor_address",
  "vinification_details",
  "recycling_information",
  "return_address",
  "alchol_by_volume",
  "beer_deg",
  "netcontent",
  "netweight",
  "site_shown_uom",
  "ingredients",
  "random_weight_flag",
  "instock",
  "promo_limit",
  "product_unique_key",
  "multibuy_items_pricesingle",
  "perfect_match",
  "servings_per_pack",
  "warning",
  "suitable_for",
  "standard_drinks",
  "environmental",
  "grape_variety",
  "retail_limit"
]

def export_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]
        
        logger.info(f"Connected to MongoDB. Exporting from {MONGO_COLLECTION_DATA}")
        
        cursor = collection.find({}).limit(200)
        total_docs = collection.count_documents({})
        export_limit = 200
        export_count = min(total_docs, export_limit)
        logger.info(f"Total documents available: {total_docs}. Exporting up to: {export_count}")
        
        with open(FILE_NAME_FULLDUMP, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers, extrasaction='ignore', delimiter='|', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            count = 0
            for doc in cursor:

                row = {}
                for header in csv_headers:
                    val = doc.get(header, "")
                    if val is None:
                        val = ""
                    
                    val_str = str(val).strip()
                    if val_str.lower() in ["na", "none"]:
                        val_str = ""
                    
                    # Clean the product description
                    if header == "product_description":
                        # Replace \xa0 with space, remove newlines, collapse multiple spaces, remove zero-width space
                        val_str = val_str.replace('\xa0', ' ').replace('\u200b', '')
                        val_str = re.sub(r'[\r\n]+', ' ', val_str)
                        val_str = re.sub(r'\s{2,}', ' ', val_str).strip()
                        
                        # Remove Disclaimer text
                        val_str = re.sub(r'Disclaimer\s*:.*', '', val_str, flags=re.IGNORECASE).strip()
                        
                        # Empty string if it's just responsive image placeholders
                        unwanted_phrases = ["Responsive A+ Content", "Responsive Image Display", "Responsive Images"]
                        if any(phrase in val_str for phrase in unwanted_phrases):
                            val_str = ""
                    
                    # Remove query parameters from image URLs
                    if header.startswith("image_url_") and "?" in val_str:
                        val_str = val_str.split("?")[0]
                        
                    row[header] = val_str
                writer.writerow(row)
                
                count += 1
                if count % 100 == 0:
                    logger.info(f"Exported {count}/{export_count} rows...")
                    
        logger.info(f"Successfully exported {count} rows to {FILE_NAME_FULLDUMP}")
        
    except Exception as e:
        logger.error(f"Error during export: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    export_data()
