from curl_cffi import requests
import json
import logging
import pymongo
from parsel import Selector
import settings
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalQuantityExtractor:
    def __init__(self):
        self.weight_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s?(kg|g|gm|gms|gram|grams|ml|l)\b',
            re.IGNORECASE
        )

        self.count_pattern = re.compile(
            r'(\d+)\s?(sachets?|bags?|tea\s*bags?|pcs?|tablets?|capsules?|cubes?|sticks?|pouches?|boxes?|jar|pack|bottles?|tins?|cans?|count|servings?)\b',
            re.IGNORECASE
        )

    def extract(self, title: str):
        if not title:
            return None

        weight_match = self.weight_pattern.search(title)
        if weight_match:
            return {
                "quantity": weight_match.group(1),
                "unit": weight_match.group(2)
            }

        count_match = self.count_pattern.search(title)
        if count_match:
            return {
                "quantity": count_match.group(1),
                "unit": count_match.group(2)
            }

        return None

class Parser:
    def __init__(self):
        self.headers = settings.headers
        
        # mongodb connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB
        self.collection_name = settings.MONGO_COLLECTION_RESPONSE
        self.product_collection_name = settings.MONGO_COLLECTION_DATA
        
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.url_collection = self.db[self.collection_name]
            self.product_collection = self.db[self.product_collection_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            
        self.grammage_extractor = FinalQuantityExtractor()

    def start(self):
        try:
            logger.info(f"Started processing. Collection: {self.product_collection_name}")
            total_docs = self.url_collection.count_documents({})
            logger.info(f"Total URLs: {total_docs}")
            
            for idx, doc in enumerate(self.url_collection.find(), 1):
                product_url = doc.get("pdp_url")
                unique_id = doc.get("unique_id")
                image_url_1 = doc.get("image_url")
                
                if not product_url or not unique_id: 
                    continue

                if self.product_collection.find_one({"pdp_url": product_url}):
                    logger.debug(f"Skipped: {product_url}")
                    continue
                
                logger.info(f"Item {idx}/{total_docs}: {product_url}")
                try:
                    response = requests.get(
                        product_url, 
                        headers=self.headers, 
                        impersonate="chrome110",
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        self.parse_item(unique_id, product_url, image_url_1, response)
                    else:
                        logger.error(f"Failed to fetch {product_url}: Status {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Request error for {product_url}: {e}")
                
        except Exception as e:
            logger.error(f"Batch error: {e}")

    def parse_item(self, unique_id, pdp_url, image_url_1, response):
        try:
            sel = Selector(response.text)
            
            product_name = sel.xpath('//div[@id="pdp_product_name"]//text()').get()
            brand = sel.xpath('//div[@class="product-header-brand-text"]//a[@id="top_brand_name"]/text()').get()
            
            # Grammage Extraction
            grammage_quantity = ""
            grammage_unit = ""
            extracted_grammage = self.grammage_extractor.extract(product_name)
            if extracted_grammage:
                grammage_quantity = str(extracted_grammage.get("quantity", ""))
                grammage_unit = str(extracted_grammage.get("unit", ""))
            
            producthierarchy_level1 = sel.xpath("(//ul[@class='jm-breadcrumbs-list']/li)[1]/a/text()").get()
            producthierarchy_level2 = sel.xpath("(//ul[@class='jm-breadcrumbs-list']/li)[2]/a/text()").get()
            producthierarchy_level3 = sel.xpath("(//ul[@class='jm-breadcrumbs-list']/li)[3]/a/text()").get()
            package_sizeof_sellingprice = sel.xpath('//tr[th[contains(text(), "Pack Of")]]/td/text()').get()
            
            breadcrumb_list = sel.xpath('//ul[@class="jm-breadcrumbs-list"]//a/text()').getall()
            breadcrumb = " > ".join(breadcrumb_list) if breadcrumb_list else ""
            
            product_description = sel.xpath("//div[@id='pdp_description']//text()[normalize-space()]").get()
            storage_instructions = sel.xpath('//tr[th[contains(text(), "Storage Category")]]/td/text()').get()
            instructionforuse = sel.xpath('//tr[th[contains(text(), "How To Use")]]/td/text()').get()
            country_of_origin = sel.xpath('//tr[th[contains(text(), "Country of Origin")]]/td/text()').get()
            
            height = sel.xpath('//tr[th[contains(text(), "Height")]]/td/text()').get()
            length = sel.xpath('//tr[th[contains(text(), "Length")]]/td/text()').get()
            width = sel.xpath('//tr[th[contains(text(), "Width")]]/td/text()').get()
            
            dimensions = ""
            if length and width and height:
                dimensions = f"{length}X{width}X{height}"
                
            manufacturer_address = sel.xpath('//tr[th[contains(text(), "Manufacturer Address")]]/td/text()').get()
            netweight = sel.xpath('//tr[th[contains(text(), "Net Weight")]]/td/text()').get()
            
            product_unique_key = f"{unique_id}P"
            
            # Pricing API Call
            regular_price = ""
            selling_price = ""
            percentage_discount = ""
            price_was = ""
            
            try:
                price_url = f"https://www.jiomart.com/catalog/productdetails/get/{unique_id}"
                price_resp = requests.get(price_url, headers=self.headers, timeout=10)
                if price_resp.status_code == 200:
                    pd = price_resp.json()
                    result = pd.get("data", {})
                    if result:
                        regular_price = result.get("mrp", "")
                        selling_price = result.get("selling_price", "")
                        percentage_discount = result.get("discount_pct", "")
                        
                        if regular_price and selling_price:
                            if float(regular_price) == float(selling_price):
                                price_was = ""
                            else:
                                price_was = regular_price
            except Exception as e:
                logger.error(f"Pricing API error for {unique_id}: {e}")

            # Rating and Review API Call
            rating = ""
            review = ""
            try:
                rating_headers = self.headers.copy()
                rating_headers['vertical'] = 'jiomart'
                rating_headers['accept'] = 'application/json'
                
                rating_url = f"https://reviews-ratings.jio.com/customer/op/v1/review/product-statistics/{unique_id}"
                rating_resp = requests.get(rating_url, headers=rating_headers, timeout=10)
                
                if rating_resp.status_code == 200:
                    details = rating_resp.json()
                    data = details.get("data", {})
                    if data:
                        rating = data.get("averageRating", "")
                        review = data.get("ratingsCount", "")
            except Exception as e:
                logger.error(f"Rating API error for {unique_id}: {e}")

            items = {
                "unique_id": str(unique_id) if unique_id else "",
                "competitor_name": "jiomart",
                "store_name": "",
                "store_addressline1": "",
                "store_addressline2": "",
                "store_suburb": "",
                "store_state": "",
                "store_postcode": "",
                "store_addressid": "",
                "extraction_date": settings.EXTRACTION_DATE,
                "product_name": str(product_name).strip() if product_name else "",
                "brand": str(brand) if brand else "",
                "brand_type": "",
                "grammage_quantity": str(grammage_quantity),
                "grammage_unit": str(grammage_unit),
                "drained_weight": "",
                "producthierarchy_level1": str(producthierarchy_level1) if producthierarchy_level1 else "",
                "producthierarchy_level2": str(producthierarchy_level2) if producthierarchy_level2 else "",
                "producthierarchy_level3": str(producthierarchy_level3) if producthierarchy_level3 else "",
                "producthierarchy_level4": "",
                "producthierarchy_level5": "",
                "producthierarchy_level6": "",
                "producthierarchy_level7": "",
                "regular_price": str(regular_price),
                "selling_price": str(selling_price),
                "price_was": str(price_was),
                "promotion_price": "",
                "promotion_valid_from": "",
                "promotion_valid_upto": "",
                "promotion_type": "",
                "percentage_discount": str(percentage_discount),
                "promotion_description": "",
                "package_sizeof_sellingprice": str(package_sizeof_sellingprice) if package_sizeof_sellingprice else "",
                "per_unit_sizedescription": "",
                "price_valid_from": "",
                "price_per_unit": "",
                "multi_buy_item_count": "",
                "multi_buy_items_price_total": "",
                "currency": "INR",
                "breadcrumb": str(breadcrumb),
                "pdp_url": str(pdp_url) if pdp_url else "",
                "variants": "",
                "product_description": str(product_description).strip() if product_description else "",
                "instructions": "",
                "storage_instructions": str(storage_instructions).strip() if storage_instructions else "",
                "preparationinstructions": "",
                "instructionforuse": str(instructionforuse).strip() if instructionforuse else "",
                "country_of_origin": str(country_of_origin).strip() if country_of_origin else "",
                "allergens": "",
                "age_of_the_product": "",
                "age_recommendations": "",
                "flavour": "",
                "nutritions": "",
                "nutritional_information": "",
                "vitamins": "",
                "labelling": "",
                "grade": "",
                "region": "",
                "packaging": "",
                "receipies": "",
                "processed_food": "",
                "barcode": "",
                "frozen": "",
                "chilled": "",
                "organictype": "",
                "cooking_part": "",
                "Handmade": "",
                "max_heating_temperature": "",
                "special_information": "",
                "label_information": "",
                "dimensions": str(dimensions),
                "special_nutrition_purpose": "",
                "feeding_recommendation": "",
                "warranty": "",
                "color": "",
                "model_number": "",
                "material": "",
                "usp": "",
                "dosage_recommendation": "",
                "tasting_note": "",
                "food_preservation": "",
                "size": "",
                "rating": str(rating),
                "review": str(review),
                "file_name_1": "",
                "image_url_1": str(image_url_1) if image_url_1 else "",
                "file_name_2": "",
                "image_url_2": "",
                "file_name_3": "",
                "image_url_3": "",
                "competitor_product_key": "",
                "fit_guide": "",
                "occasion": "",
                "material_composition": "",
                "style": "",
                "care_instructions": "",
                "heel_type": "",
                "heel_height": "",
                "upc": "",
                "features": "",
                "dietary_lifestyle": "",
                "manufacturer_address": str(manufacturer_address).strip() if manufacturer_address else "",
                "importer_address": "",
                "distributor_address": "",
                "vinification_details": "",
                "recycling_information": "",
                "return_address": "",
                "alchol_by_volume": "",
                "beer_deg": "",
                "netcontent": "",
                "netweight": str(netweight).strip() if netweight else "",
                "site_shown_uom": "",
                "ingredients": "",
                "random_weight_flag": "",
                "instock": "",
                "promo_limit": "",
                "product_unique_key": str(product_unique_key),
                "multibuy_items_pricesingle": "",
                "perfect_match": "",
                "servings_per_pack": "",
                "Warning": "",
                "suitable_for": "",
                "standard_drinks": "",
                "environmental": "",
                "grape_variety": "",
                "retail_limit": ""
            }
            
            try:
                self.product_collection.insert_one(items)
                logger.debug(f"Saved parsed data for {pdp_url}")
            except Exception as e:
                logger.error(f"Save error for parsed data: {e}")

        except Exception as e:
            logger.error(f"Error parsing {pdp_url}: {e}")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()