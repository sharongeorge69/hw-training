from curl_cffi import requests
import logging
import pymongo
from parsel import Selector
from settings import headers, headers_price_api, MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, EXTRACTION_DATE, CRAWLER_URL, json_data_price
import re
from items import ProductDataItem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        self.headers = headers
        self.headers_price_api = headers_price_api
        # mongodb connection
        self.mongo_uri = MONGO_URI
        self.db_name = MONGO_DB
        self.collection_name = MONGO_COLLECTION_RESPONSE
        self.product_collection_name = MONGO_COLLECTION_DATA
        
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.url_collection = self.db[self.collection_name]
            self.product_collection = self.db[self.product_collection_name]
            
            # Create a unique index for unique_id
            self.product_collection.create_index("unique_id", unique=True)
            
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")

    def start(self):
        try:
            logger.info(f"Started processing. Collection: {self.product_collection_name}")
            total_docs = self.url_collection.count_documents({})
            logger.info(f"Total URLs: {total_docs}")
            
            for idx, doc in enumerate(self.url_collection.find(), 1):
                product_url = doc.get("pdp_url")
                unique_id = doc.get("unique_id")
                
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
                        self.parse_item(unique_id, product_url, response)
                    else:
                        logger.error(f"Failed to fetch {product_url}: Status {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Request error for {product_url}: {e}")
                
        except Exception as e:
            logger.error(f"Batch error: {e}")

    def parse_item(self, unique_id, pdp_url, response):
        try:
            sel = Selector(response.text)
            
            # XPATH
            PRODUCT_NAME_XPATH = '//div[@id="pdp_product_name"]//text()'
            BRAND_XPATH = '//div[@class="product-header-brand-text"]//a[@id="top_brand_name"]/text()'
            PRODUCTHIERARCHY_LEVEL1_XPATH = "(//ul[@class='jm-breadcrumbs-list']/li)[1]/a/text()"
            PRODUCTHIERARCHY_LEVEL2_XPATH = "(//ul[@class='jm-breadcrumbs-list']/li)[2]/a/text()"
            PRODUCTHIERARCHY_LEVEL3_XPATH = "(//ul[@class='jm-breadcrumbs-list']/li)[3]/a/text()"
            PACKAGE_SIZEOF_SELLINGPRICE_XPATH = '//tr[th[contains(text(), "Pack Of")]]/td/text()'
            BREADCRUMB_LIST_XPATH = '//ul[@class="jm-breadcrumbs-list"]//a/text()'
            DESC_NODES_XPATH = "//div[@id='pdp_description']//text()[not(ancestor::button) and not(ancestor::style) and not(ancestor::script)]"
            STORAGE_INSTRUCTIONS_XPATH = '//tr[th[contains(text(), "Storage Category")]]/td/text()'
            INSTRUCTIONFORUSE_XPATH = '//tr[th[contains(text(), "How To Use")]]/td/text()'
            COUNTRY_OF_ORIGIN_XPATH = '//tr[th[contains(text(), "Country of Origin")]]/td/text()'
            HEIGHT_XPATH = '//tr[th[contains(text(), "Height")]]/td/text()'
            LENGTH_XPATH = '//tr[th[contains(text(), "Length")]]/td/text()'
            WIDTH_XPATH = '//tr[th[contains(text(), "Width")]]/td/text()'
            IMG_URLS_XPATH = (
                "//div[contains(@class,'product-image-carousel-thumb')]"
                "//div[contains(@class,'swiper-thumb-slides')]//img/@data-src | "
                "//div[contains(@class,'product-image-carousel-thumb')]"
                "//div[contains(@class,'swiper-thumb-slides')]//img/@src"
            )
            MANUFACTURER_ADDRESS_XPATH = '//tr[th[contains(text(), "Manufacturer Address")]]/td/text()'
            NETWEIGHT_XPATH = '//tr[th[contains(text(), "Net Weight")]]/td/text()'
            ALTERNATE_ID_XPATH = '//div[@id="crfe_widget"]/@data-product-id'

            # EXTRACT
            product_name = sel.xpath(PRODUCT_NAME_XPATH).extract_first()
            brand = sel.xpath(BRAND_XPATH).extract_first()
            
            # Grammage Extraction
            grammage_quantity = ""
            grammage_unit = ""
            site_shown_uom = ""
            if product_name:
                weight_match = re.search(r'(\d+(?:\.\d+)?)\s?(kg|g|gm|gms|gram|grams|grms|ml|l)\b', product_name, re.IGNORECASE)
                if weight_match:
                    grammage_quantity = str(weight_match.group(1))
                    grammage_unit = str(weight_match.group(2))
                    site_shown_uom = str(product_name).strip()
                else:
                    count_match = re.search(r'(\d+)\s?(sachets?|bags?|tea\s*bags?|pcs?|tablets?|capsules?|cubes?|sticks?|pouches?|boxes?|jar|pack|bottles?|tins?|cans?|count|servings?)\b', product_name, re.IGNORECASE)
                    if count_match:
                        grammage_quantity = str(count_match.group(1))
                        grammage_unit = str(count_match.group(2))
                        site_shown_uom = str(product_name).strip()
                    else:
                        grammage_quantity = "1"
                        grammage_unit = "pack"
            else:
                grammage_quantity = "1"
                grammage_unit = "pack"
            
            producthierarchy_level1 = sel.xpath(PRODUCTHIERARCHY_LEVEL1_XPATH).extract_first()
            producthierarchy_level2 = sel.xpath(PRODUCTHIERARCHY_LEVEL2_XPATH).extract_first()
            producthierarchy_level3 = sel.xpath(PRODUCTHIERARCHY_LEVEL3_XPATH).extract_first()
            package_sizeof_sellingprice = sel.xpath(PACKAGE_SIZEOF_SELLINGPRICE_XPATH).extract_first()
            
            breadcrumb_list = sel.xpath(BREADCRUMB_LIST_XPATH).extract()
            breadcrumb = " > ".join(breadcrumb_list) if breadcrumb_list else ""
            
            desc_nodes = sel.xpath(DESC_NODES_XPATH).extract()
            product_description = " ".join(t.strip() for t in desc_nodes if t.strip())
            storage_instructions = sel.xpath(STORAGE_INSTRUCTIONS_XPATH).extract_first()
            instructionforuse = sel.xpath(INSTRUCTIONFORUSE_XPATH).extract_first()
            country_of_origin = sel.xpath(COUNTRY_OF_ORIGIN_XPATH).extract_first()
            
            height = sel.xpath(HEIGHT_XPATH).extract_first()
            length = sel.xpath(LENGTH_XPATH).extract_first()
            width = sel.xpath(WIDTH_XPATH).extract_first()
            
            dimensions = ""
            if length and width and height:
                dimensions = f"{length}X{width}X{height}"
                
            img_urls = sel.xpath(IMG_URLS_XPATH).extract()
            img_urls = list(dict.fromkeys(img_urls))
            img_urls = img_urls[1:7]
            image_url_1 = img_urls[0] if len(img_urls) > 0 else ""
            image_url_2 = img_urls[1] if len(img_urls) > 1 else ""
            image_url_3 = img_urls[2] if len(img_urls) > 2 else ""
            image_url_4 = img_urls[3] if len(img_urls) > 3 else ""
            image_url_5 = img_urls[4] if len(img_urls) > 4 else ""
            image_url_6 = img_urls[5] if len(img_urls) > 5 else ""
            
            manufacturer_address = sel.xpath(MANUFACTURER_ADDRESS_XPATH).extract_first()
            netweight = sel.xpath(NETWEIGHT_XPATH).extract_first()
            
            product_unique_key = f"{unique_id}P"
            
            # Pricing API Call (TREX Search API)
            regular_price = ""
            selling_price = ""
            percentage_discount = ""
            price_was = ""
            alternate_id = ""
            
            try:
                # Prepare payload for specific product
                payload = json_data_price.copy()
                payload['filter'] = f'attributes.product_id:ANY("{unique_id}")'
                payload['pageSize'] = 1
                
                price_resp = requests.post(CRAWLER_URL, headers=self.headers, json=payload, timeout=15, impersonate="chrome110")
                if price_resp.status_code == 200:
                    data = price_resp.json()
                    results = data.get("results", [])
                    
                    if results:
                        product = results[0].get("product", {})
                        variants = product.get("variants", [])
                        if variants:
                            variant = variants[0]
                            attributes = variant.get("attributes", {})
                            buybox_mrp = attributes.get("buybox_mrp", {}).get("text", [])
                            # Search for TXCF in buybox_mrp
                            txcf_data = next((entry for entry in buybox_mrp if entry.startswith("TXCF|")), None)
                            if not txcf_data:
                                # Fallback to any region that has pricing data
                                txcf_data = next((entry for entry in buybox_mrp if "|" in entry and len(entry.split("|")) > 5), None)
                            
                            if txcf_data:
                                parts = txcf_data.split("|")
                                if len(parts) > 5:
                                    regular_price = parts[4]
                                    selling_price = parts[5]
                                    # Use index 8 for percentage discount
                                    percentage_discount = parts[8] if len(parts) > 8 else ""
                else:
                    logger.warning(f"TREX API error for {unique_id}: Status {price_resp.status_code}")

                if regular_price and selling_price:
                    if float(regular_price) == float(selling_price):
                        price_was = ""
                    else:
                        price_was = regular_price
                        
                if regular_price:
                    regular_price = f"{float(regular_price):.2f}"
                if selling_price:
                    selling_price = f"{float(selling_price):.2f}"
                if price_was:
                    price_was = f"{float(price_was):.2f}"
            except Exception as e:
                logger.error(f"Pricing API error for {unique_id}: {e}")

            # Extract alternate_id from HTML for Rating API
            alternate_id = sel.xpath(ALTERNATE_ID_XPATH).get()
            
            # If not found in crfe_widget, look in gtmEvents data-id (unique_id often matches)
            if not alternate_id:
                alternate_id = unique_id

            # Rating and Review API Call
            rating = ""
            review = ""
            try:
                if alternate_id:
                    rating_headers = {
                        'vertical': 'jiomart',
                        'accept': 'application/json',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                    }
                    
                    rating_url = f"https://reviews-ratings.jio.com/customer/op/v1/review/product-statistics/{alternate_id}"
                    rating_resp = requests.get(rating_url, headers=rating_headers, timeout=10)
                    
                    if rating_resp.status_code == 200:
                        details = rating_resp.json()
                        data = details.get("data", {})
                        if data:
                            rating = data.get("averageRating", "")
                            review = data.get("ratingsCount", "")
            except Exception as e:
                logger.error(f"Rating API error for {unique_id} (alternate_id: {alternate_id}): {e}")

            items = {
                "unique_id": str(unique_id) if unique_id else "",
                "competitor_name": "jiomart",
                "extraction_date": EXTRACTION_DATE,
                "product_name": str(product_name).strip() if product_name else "",
                "brand": str(brand) if brand else "",
                "grammage_quantity": str(grammage_quantity),
                "grammage_unit": str(grammage_unit),
                "producthierarchy_level1": str(producthierarchy_level1) if producthierarchy_level1 else "",
                "producthierarchy_level2": str(producthierarchy_level2) if producthierarchy_level2 else "",
                "producthierarchy_level3": str(producthierarchy_level3) if producthierarchy_level3 else "",
                "regular_price": str(regular_price) if regular_price else "",
                "selling_price": str(selling_price) if selling_price else "",
                "price_was": str(price_was) if price_was else "",
                "percentage_discount": str(percentage_discount) if percentage_discount else "",
                "package_sizeof_sellingprice": str(package_sizeof_sellingprice) if package_sizeof_sellingprice else "",
                "currency": "INR",
                "breadcrumb": str(breadcrumb),
                "pdp_url": str(pdp_url) if pdp_url else "",
                "product_description": str(product_description).strip() if product_description else "",
                "storage_instructions": str(storage_instructions).strip() if storage_instructions else "",
                "instructionforuse": str(instructionforuse).strip() if instructionforuse else "",
                "country_of_origin": str(country_of_origin).strip() if country_of_origin else "",
                "dimensions": str(dimensions),
                "rating": str(rating),
                "review": str(review),
                "image_url_1": str(image_url_1),
                "image_url_2": str(image_url_2),
                "image_url_3": str(image_url_3),
                "image_url_4": str(image_url_4),
                "image_url_5": str(image_url_5),
                "image_url_6": str(image_url_6),
                "manufacturer_address": str(manufacturer_address).strip() if manufacturer_address else "",
                "netweight": str(netweight).strip() if netweight else "",
                "site_shown_uom": str(site_shown_uom),
                "instock": "True",
                "product_unique_key": str(product_unique_key),
            }
            
            # Validation logic
            try:
                # Instantiate and validate
                product_item = ProductDataItem(**items)
                product_item.validate()
                
                # Save to MongoDB
                self.product_collection.insert_one(items)
                logger.info(f"Saved: {pdp_url}")
            except Exception as e:
                logger.error(f"Validation or Save error for {pdp_url}: {e}")

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
