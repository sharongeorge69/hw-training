import re
import html
import pymongo
import logging
import requests
import fastenal_settings as settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FastenalParser:
    def __init__(self):
        self.headers = settings.HEADERS
        self.cookies = settings.COOKIES
        self.endpoint_url = settings.ENDPOINT_URL
        #mongodb connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.DB_NAME
        self.pdp_urls = settings.PRODUCT_COLLECTION_NAME
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.pdp_collection = self.db[self.pdp_urls]
            self.parsed_collection = self.db[settings.PARSED_COLLECTION_NAME]
            # Create unique index on url and sku
            self.parsed_collection.create_index([("url", 1), ("sku", 1)], unique=True)
            logging.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    #Fetch product data from API
    def fetch_pdp_urls(self, page_url, sku):
        payload = {
           "attributeFilters": {},
           "pageUrl": page_url,
           "productDetails": True,
           "sku": [sku]
        }
        try:
            response = requests.post(self.endpoint_url, headers=self.headers, cookies=self.cookies, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch {sku}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {sku}: {e}")
            return None

    def clean_html(self, raw_html):
        if not raw_html:
            return ""
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, ' ', raw_html)
        return html.unescape(cleantext).strip()

    #Parse product data
    def parse_product_data(self, data, product_url=None):
        if not data or "productDetail" not in data:
            return None
        
        detail = data["productDetail"]
        
        # Description
        notes = detail.get("notes", {})
        desc_parts = []
        if notes.get("mp_publicNotes"):
            desc_parts.append(self.clean_html(notes.get("mp_publicNotes")))
        if notes.get("mp_complianceNotes"):
             desc_parts.append(self.clean_html(notes.get("mp_complianceNotes")))
        if notes.get("mp_bulletPoints"):
            desc_parts.append(self.clean_html(notes.get("mp_bulletPoints")))
        if notes.get("mp_applicationUse"):
            desc_parts.append(self.clean_html(notes.get("mp_applicationUse")))
            
        full_description = " ".join([p for p in desc_parts if p])
        full_description = " ".join(full_description.split())

        parsed_item = {
            "sku": detail.get("sku"),
            "title": detail.get("mp_des"),
            "manufacturer": detail.get("mfr"),
            "part_number": detail.get("manufacturerPartNo"),
            "url": product_url,
            "unspsc_code": detail.get("unspscCode"),
            "description": full_description,
            "brand": detail.get("brNm"),
            "image_url": detail.get("imgOne"),
            "price": None,
            "breadcrumbs": [],
        }

        # Price
        if "pdd" in detail:
            for p in detail["pdd"]:
                if p.get("dataName") == "Online Price:":
                    parsed_item["price"] = p.get("pr")
                    break

        # Breadcrumbs
        bc = data.get("breadCrumbs", {})
        bc_parts = [
            "Home",
            "All Products",
            bc.get("mp_categoryLevelOneLabel"),
            bc.get("mp_categoryLevelTwoLabel"),
            bc.get("mp_categoryLevelThreeLabel")
        ]
        parsed_item["breadcrumbs"] = " > ".join([b for b in bc_parts if b])

        # ProductAttributes 
        if "catAtt" in detail:
            for att in detail["catAtt"]:
                name = att.get("mp_nm")
                value = att.get("mp_vl")
                if name and value:
                    clean_key = name.strip().lower().replace(" ", "_").replace(".", "").replace("/", "_")
                    parsed_item[clean_key] = value

        return parsed_item

    def parse(self):
        category_level_three = self.pdp_collection.find({"categoryLevelThree": "Duct Tape"})
        count = 0
        total = self.pdp_collection.count_documents({"categoryLevelThree": "Duct Tape"})
        logger.info(f"Found {total} products to parse.")
        
        for document in category_level_three:
            page_url = document.get("pageUrl")
            sku = document.get("sku")
            product_url = document.get("url")
            
            if not page_url or not sku:
                continue

            logger.info(f"Processing ({count+1}/{total}) SKU: {sku}")
            api_data = self.fetch_pdp_urls(page_url, sku)
            if api_data:
                product_data = self.parse_product_data(api_data, product_url)
                #Save product data to mongodb
                if product_data:
                    try:
                        self.parsed_collection.update_one(
                            {"sku": sku},
                            {"$set": product_data},
                            upsert=True
                        )
                        logger.info(f"Saved {sku}")
                        count += 1
                    except Exception as e:
                        logger.error(f"Error saving {sku}: {e}")
        return count

if __name__ == "__main__":
    parser = FastenalParser()
    parser.parse()