import csv
import logging
import re
import json
from parsel import Selector
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_RAW_RESPONSE, FILE_NAME_FULLDUMP, EXPORT_LIMIT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CSV_HEADERS = [
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

def format_price(price):
    try:
        if price and str(price).strip():
            val = float(price)
            return f"{val:.2f}"
    except (ValueError, TypeError):
        pass
    return ""

def clean_brand(brand):
    if not brand:
        return ""
    return str(brand).replace('®', '').strip()

def export_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]
        raw_collection = db[MONGO_COLLECTION_RAW_RESPONSE]
        
        logger.info(f"Connected to MongoDB. Exporting from {MONGO_COLLECTION_DATA}")
        
        cursor = collection.find({}).limit(EXPORT_LIMIT)
        total_docs = collection.count_documents({})
        export_count = min(total_docs, EXPORT_LIMIT)
        logger.info(f"Total documents available: {total_docs}. Exporting up to: {export_count}")
        
        with open(FILE_NAME_FULLDUMP, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, extrasaction='ignore', delimiter='|', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            count = 0
            for doc in cursor:
                # Local extraction logic
                unique_id = doc.get("unique_id")
                price_per_unit = doc.get("price_per_unit")
                
                raw_doc = raw_collection.find_one({"unique_id": unique_id})
                if raw_doc:
                    html_content = raw_doc.get("html_content")
                    if html_content:
                        sel = Selector(text=html_content)
                        # Extract unique_id from digitalData
                        try:
                            script = sel.xpath("//script[contains(text(),'digitalData')]/text()").get()
                            if script:
                                json_match = re.search(r'digitalData\s*=\s*(\{.*?\});', script, re.S)
                                if json_match:
                                    data = json.loads(json_match.group(1))
                                    page_name = data.get("page", {}).get("pageInfo", {}).get("pageName", "")
                                    id_match = re.search(r'Product Detail:(\d+)', page_name)
                                    if id_match:
                                        unique_id = id_match.group(1)
                        except Exception as e:
                            logger.warning(f"Could not extract unique_id for {doc.get('unique_id')}: {e}")

                        # Extract price_per_unit
                        PRICE_PER_UNIT_XPATH = "normalize-space(//span[contains(@class,'price__base')])"
                        extracted_ppu = sel.xpath(PRICE_PER_UNIT_XPATH).extract_first()
                        if extracted_ppu:
                            price_per_unit = extracted_ppu

                row = {}
                for header in CSV_HEADERS:
                    if header == "unique_id":
                        val = unique_id
                    elif header == "price_per_unit":
                        val = price_per_unit
                    else:
                        val = doc.get(header, "")
                    
                    if val is None:
                        val = ""
                    
                    val_str = str(val).strip()
                    
                    if header in ["regular_price", "selling_price", "price_was"]:
                        val_str = format_price(val_str)
                    
                    elif header == "brand":
                        val_str = clean_brand(val_str)
                    
                    row[header] = val_str
                    
                writer.writerow(row)
                count += 1
                if count % 100 == 0:
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