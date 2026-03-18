import csv
import logging
import re
import json
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME_FULLDUMP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EXPORT_LIMIT = 200

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

ALLERGEN_MAP = {
    "Eggs": "Eieren",
    "Mustard": "Mosterd",
    "Fish": "Vis",
    "Gluten": "Gluten",
    "Milk": "Melk",
    "Soy": "Soja",
    "Peanuts": "Pindanoten",
    "Sulphites": "Sulfieten",
    "Treenuts": "Noten",
    "Lupin": "Lupine",
    "Sesameseeds": "Sesamzaden",
    "Celery": "Selder"
}

TECH_PROMO_MAP = {
    "100871COLR": "12+6 GRATIS",
    "100878COLR": "-10% vanaf 12 st, -20% vanaf 24 st",
    "1707COLR": "8+4 GRATIS",
    "100872COLR": "5+1 GRATIS",
    "100882COLR": "-20% vanaf 12 st",
    "100883COLR": "-25% vanaf 3 st",
    "100998COLR": "1+1 GRATIS",
    "100879COLR": "1+1 GRATIS",
    "1022COLR": "-25% vanaf 2 st"
}

def format_extraction_date(date_str):
    if not date_str:
        return ""
 
    return date_str.replace('_', '-')

def format_validity_date(date_str):
    if not date_str:
        return ""
    # Convert DD-MM-YYYY to D/M/YYYY (removing leading zeros)
    # e.g., 11-03-2026 -> 11/3/2026
    match = re.match(r'(\d{1,2})-(\d{1,2})-(\d{4})', date_str)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = match.group(3)
        return f"{day}/{month}/{year}"
    return date_str

def clean_description(description_raw):
    if not description_raw:
        return ""
    
    # normalize hyphen line breaks
    text = re.sub(r'-\n', '-', description_raw)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    clean_lines = []
    for line in lines:
        # remove bullet markers
        line = re.sub(r'^[\*\-\•]\s*', '', line)
        # remove trailing commas
        line = line.rstrip(',')
        clean_lines.append(line)
        
    # detect bullet style vs paragraph style
    if "*" in description_raw or "•" in description_raw:
        description = ", ".join(clean_lines)
    else:
        description = " ".join(clean_lines)
        
    # cleanup extra punctuation
    description = re.sub(r'\s+,', ',', description)
    description = re.sub(r',+', ',', description)
    description = re.sub(r'\s+', ' ', description).strip()
    
    return description

def translate_allergens(allergens_str):
    if not allergens_str:
        return ""
    
    items = [a.strip() for a in allergens_str.split(',') if a.strip()]
    translated = []
    for item in items:
        translated.append(ALLERGEN_MAP.get(item, item))
    
    return ", ".join(translated)

def format_price(price):
    try:
        if price and str(price).strip():
            # Handle float or string with comma/Euro
            p_val = str(price).replace('€', '').replace(',', '.').strip()
            val = float(p_val)
            # Truncate to 2 decimal places (no rounding)
            truncated = int(val * 100) / 100.0
            return f"{truncated:.2f}"
    except (ValueError, TypeError):
        pass
    return ""

def clean_promotion_description(promo_desc):
    if not promo_desc:
        return ""
    # change 24.0 to just 24
    return re.sub(r'(\d+)\.0(\s+)', r'\1\2', promo_desc)

def extract_grammage(site_shown_uom):
    """
    Extract grammage_quantity and grammage_unit from site_shown_uom.
    Handles complex patterns like '10x20cl'.
    """
    quantity = ""
    unit = ""
    if site_shown_uom:
        site_shown_uom = str(site_shown_uom).strip()
        # match digits, commas, dots and 'x' for quantity, followed by letters for unit
        match = re.search(r'([\d,\.xX]+)\s*([a-zA-Z]+)', site_shown_uom)
        if match:
            quantity = match.group(1).strip().replace(',', '.')
            unit = match.group(2).strip()
    return quantity, unit

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
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, extrasaction='ignore', delimiter='|', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            count = 0
            for doc in cursor:
                row = {}
                # Load product details if they exist to apply advanced cleanups
                product_details_raw = doc.get("product_details", "")
                try:
                    product_details = json.loads(product_details_raw) if product_details_raw else {}
                except:
                    product_details = {}

                # Get site_shown_uom for robust grammage extraction
                site_shown_uom = doc.get("site_shown_uom", "")
                g_qty, g_unit = extract_grammage(site_shown_uom)

                # Get techPromoId mapping if it exists
                tech_promo_id = doc.get("techPromoId", "")
                tech_promo_text = TECH_PROMO_MAP.get(tech_promo_id, "")

                for header in CSV_HEADERS:
                    val = doc.get(header, "")
                    if val is None:
                        val = ""
                    
                    val_str = str(val).strip()
                    if val_str.lower() in ["na", "none", "nan"]:
                        val_str = ""
                    
                    # Apply specific transformations
                    if header == "product_description":
                        # Use the advanced description cleanup logic
                        desc_raw = product_details.get("description", "")
                        val_str = clean_description(desc_raw)
                    
                    elif header == "allergens":
                        val_str = translate_allergens(val_str)
                    
                    elif header in ["regular_price", "selling_price"]:
                        val_str = format_price(val_str)
                    
                    elif header == "promotion_description":
                        val_str = clean_promotion_description(val_str)
                        if tech_promo_text:
                            if val_str:
                                val_str = f"{val_str}, {tech_promo_text}"
                            else:
                                val_str = tech_promo_text
                    
                    elif header == "extraction_date":
                        val_str = format_extraction_date(val_str)
                    
                    elif header in ["promotion_valid_from", "promotion_valid_upto", "price_valid_from"]:
                        val_str = format_validity_date(val_str)
                    
                    elif header == "grammage_quantity":
                        val_str = g_qty
                    
                    elif header == "grammage_unit":
                        val_str = g_unit
                    
                    elif header == "currency":
                        if val_str.lower() == "euro":
                            val_str = "EUR"
                    
                    elif header == "site_shown_uom":
                        val_str = val_str.replace(',', '.')
                    
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
        client.close()

if __name__ == '__main__':
    export_data()
