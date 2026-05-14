import logging
import time
import requests
from pymongo import MongoClient
import pymongo
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, headers, PROJECT_NUMBER, EXTRACTION_DATE
from items import ProjectItem

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self):
        self.headers = headers
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        
        self.url_collection.create_index("project_number", unique=True)
        logger.info("Connected to MongoDB") 

    def parse_response(self, response_json, project_number):
        if not response_json:
            logger.error(f"Received empty response for {project_number}")
            return False

        try:
            projects = response_json.get("response", {}).get("projects", [])
            
            if not projects:
                logger.warning(f"No projects found for number {project_number}")
                return False

            saved_count = 0
            for project in projects:
                number = str(project.get("number"))
                name_info = project.get("name", {})
                english_name = name_info.get("englishName", "")
                
                item = {
                    "project_number": number,
                    "project_name": english_name,
                    "extraction_date": EXTRACTION_DATE
                }
                
                try:
                    project_item = ProjectItem(**item)
                    project_item.validate()
                    self.url_collection.insert_one(item)
                    saved_count += 1
                except pymongo.errors.DuplicateKeyError:
                    logger.debug(f"  Project {number} already exists in database.")
                except Exception as e:
                    logger.error(f"  Save error for project {number}: {e}")
            
            if saved_count > 0:
                logger.info(f"Saved {saved_count} new projects for search '{project_number}'.")
            return True

        except Exception as e:
            logger.error(f"Error parsing response for {project_number}: {e}")
            return False

    def refresh_token(self):
        from playwright.sync_api import sync_playwright
        logger.info("  Launching browser to refresh token...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                page = context.new_page()
                
                target_url = "https://dubailand.gov.ae/en/eservices/real-estate-project-status-landing/real-estate-project-status/"
                page.goto(target_url, wait_until="networkidle")
                
                token = page.evaluate("sessionStorage.getItem('mashrooi-token')")
                
                if not token:
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

    def start(self):
        max_retries = 3
        logger.info(f"Starting crawler for {len(PROJECT_NUMBER)} project numbers...")
        
        for number in PROJECT_NUMBER:
            url = f"https://b2c.dubailand.gov.ae/mashrooi/projects/searchlite?keywords={number}&"
            logger.info(f"Crawling project number: {number}")
            
            success = False
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, headers=self.headers, timeout=20)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if self.parse_response(data, number):
                                success = True
                                break
                            else:
                                success = True
                                break
                        except Exception as json_e:
                            logger.error(f"  JSON decode error for {number}: {json_e}")
                    elif response.status_code == 401:
                        logger.warning(f"  Token expired (401). Attempting to refresh...")
                        new_token = self.refresh_token()
                        if new_token:
                            self.headers['token'] = new_token
                            logger.info("  Token refreshed successfully.")
                            # Retry with new token immediately
                            continue
                        else:
                            logger.error("  Failed to refresh token.")
                    else:
                        logger.warning(f"  Attempt {attempt + 1} failed for {number} with status code {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"  Attempt {attempt + 1} failed for {number} with error: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            if not success:
                logger.error(f"Failed to crawl {number} after {max_retries} attempts")

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass

if __name__ == "__main__":
    crawler_obj = Crawler()
    try:
        crawler_obj.start()
    finally:
        crawler_obj.close()
