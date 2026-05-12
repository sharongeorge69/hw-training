import time
import requests
from pymongo import MongoClient
from datetime import datetime
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA,
    headers, headers_mollak, CONSUMER_ID
)

# Configure Logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.headers = headers
        self.headers_mollak = headers_mollak
        
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        
        # Create indexes
        self.product_collection.create_index("unique_id", unique=True)
        logger.info("Connected to MongoDB")

    def fetch_json(self, url, headers, params=None):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=20)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 401:
                    logger.warning(f"  Token expired (401). Attempting to refresh...")
                    new_token = self.refresh_token()
                    if new_token:
                        self.headers['token'] = new_token
                        headers['token'] = new_token
                        logger.info("  Token refreshed successfully.")
                        # Retry with new token immediately
                        continue
                    else:
                        logger.error("  Failed to refresh token.")
                else:
                    logger.error(f"  Failed [{resp.status_code}] for {url}")
            except Exception as e:
                logger.warning(f"  Attempt {attempt + 1} failed for {url}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
        return None

    def refresh_token(self):
        from playwright.sync_api import sync_playwright
        logger.info("  Launching browser to refresh token...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                page = context.new_page()
                
                # Navigate to the landing page that generates the token
                target_url = "https://dubailand.gov.ae/en/eservices/real-estate-project-status-landing/real-estate-project-status/"
                page.goto(target_url, wait_until="networkidle", timeout=60000)
                
                # The token is stored in sessionStorage
                token = page.evaluate("sessionStorage.getItem('mashrooi-token')")
                
                if not token:
                    # Try to trigger a search if token not immediately available
                    try:
                        page.type("input[name='keywords']", "1555")
                        page.keyboard.press("Enter")
                        time.sleep(5)
                        token = page.evaluate("sessionStorage.getItem('mashrooi-token')")
                    except:
                        pass
                
                browser.close()
                return token
        except Exception as e:
            logger.error(f"  Error during token refresh: {e}")
            return None

    def format_date(self, date_str):
        if not date_str:
            return None
        try:
            # Expected input: 2024-04-25T00:00:00
            dt = datetime.fromisoformat(date_str.split('T')[0])
            return dt.strftime("%d/%m/%Y")
        except:
            return date_str

    def start(self):
        total = self.url_collection.count_documents({})
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(self.url_collection.find(), 1):
            project_number = doc.get("project_number")
            if not project_number:
                continue

            unique_id = str(project_number)
            logger.info(f"Processing Item {idx}/{total}: {unique_id}")
            
            # 1. Fetch Mashrooi Details
            mashrooi_url = f"https://b2c.dubailand.gov.ae/mashrooi/projects/{unique_id}"
            mashrooi_data = self.fetch_json(mashrooi_url, self.headers)
            
            # 2. Fetch Mollak Details
            mollak_url = f"https://gateway.dubailand.gov.ae/mollak/internal/integration/managementcompany/project/{unique_id}"
            mollak_params = {'consumer-id': CONSUMER_ID}
            mollak_data = self.fetch_json(mollak_url, self.headers_mollak, params=mollak_params)
            
            if mashrooi_data or mollak_data:
                self.parse_item(unique_id, mashrooi_data, mollak_data)
            else:
                logger.error(f"  No data found for {unique_id}")

    def parse_item(self, unique_id, mashrooi_data, mollak_data):
        try:
            item = {
                "unique_id": unique_id,
                "inspection_details": [],
                "developer_details": {
                    "developer_name": None,
                    "developer_number": None,
                    "status": None,
                    "phone": None,
                    "email": None,
                    "website": None
                },
                "management_companies": {
                    "company_name": None,
                    "company_number": None,
                    "phone": None,
                    "mobile": None,
                    "email": None,
                    "address": None
                },
                "escrow_account": {
                    "bank_name": None,
                    "escrow": None
                }
            }

            # --- Map Mashrooi Data ---
            if mashrooi_data and "response" in mashrooi_data:
                res = mashrooi_data["response"]
                proj = res.get("project", {})
                title = proj.get("title", {})
                
                dev = title.get("developer", {})
                if not dev:
                    dev = res.get("developer", {})

                if dev:
                    contact = dev.get("contact", {})
                    item["developer_details"] = {
                        "developer_name": dev.get("name", {}).get("englishName"),
                        "developer_number": dev.get("number"),
                        "status" : "Active",
                        "phone": contact.get("phone"),
                        "email": contact.get("email"),
                        "website": contact.get("url")
                    }
                item["status"] = title.get("status", {}).get("englishName")

                # Escrow Account (from title)
                item["escrow_account"] = {
                    "bank_name": title.get("escrowAgent", {}).get("englishName"),
                    "escrow": title.get("escrowAccount")
                }

                # Inspection Details (Map all inspections)
                inspections = res.get("inspections", [])
                inspection_list = []
                for j, insp in enumerate(inspections):
                    previous = inspections[j+1] if j + 1 < len(inspections) else None
                    inspection_list.append({
                        "inspection_date": self.format_date(insp.get("date")),
                        "current_progress": f"{insp.get('percentage')}%" if insp.get('percentage') is not None else None,
                        "previous_inspection": f"{previous.get('percentage')}%" if previous and previous.get('percentage') is not None else None,
                        "inspection_images": [m.get("mediaUrl") for m in insp.get("media", []) if m.get("mediaType") == "Image"]
                    })
                item["inspection_details"] = inspection_list

            if mollak_data and "response" in mollak_data:
                mollak_res = mollak_data["response"]
                items = mollak_res.get("items", [])
                if items:
                    comp = items[0]
                    item["management_companies"] = {
                        "company_name": comp.get("company", {}).get("nameEn"),
                        "company_number": comp.get("licenseNumber"),
                        "phone": comp.get("phone"),
                        "mobile": comp.get("mobile"),
                        "email": comp.get("email"),
                        "address": comp.get("address")
                    }

            # Save to MongoDB
            self.product_collection.update_one(
                {"unique_id": unique_id},
                {"$set": item},
                upsert=True
            )
            logger.info(f"    Saved: {unique_id}")
            
        except Exception as e:
            logger.error(f"    Error parsing {unique_id}: {e}")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    parser_obj = Parser()
    try:
        parser_obj.start()
    finally:
        parser_obj.close()
