import requests
from parsel import Selector
import logging
import jcpenney_settings as settings
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Category:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[settings.MONGO_DB]
        self.collection = self.db[settings.MONGO_COLLECTION_CATEGORY]
        
        #unique index on URL
        self.collection.create_index("url", unique=True)
        self.headers = settings.HEADERS
        self.sitemap_url = settings.SITEMAP_URL
        
    def start(self):
        try:
            # Fetch Sitemap Page
            response = requests.get(
                self.sitemap_url, 
                headers=self.headers, 
                timeout=10
            )
            response.raise_for_status()
            if response.status_code == 200:
                self.parse_sitemap(response)
            
        except Exception as e:
            logger.error("Error fetching sitemap: %s", e)
            return
    def parse_sitemap(self, response):
        try:
            # Parse Sitemap Page
            selector = Selector(text=response.text)
            # linkfarm IDs(required catergory)for each category
            CATEGORY_LINKFARMS = {
                "Women": ["2", "4"],
                "Men": ["2", "3"],
                "Juniors": ["1", "5"],
                "Kids": ["1", "2"],
                "Jewelry & Watches": ["1", "2", "3", "5"],
                "Handbags": ["0", "1"]
            }
            #main category XPATH
            CATEGORY_XPATH = '//a[@class="deptLink PTZFD"]'
            category_nodes = selector.xpath(CATEGORY_XPATH)
            
            for node in category_nodes:
                aria_label = node.xpath('./@aria-label').extract_first()
                href = node.xpath('./@href').extract_first()
                
                if aria_label in CATEGORY_LINKFARMS and href:
                    url = f"https://www.jcpenney.com{href}"
                    logger.info("Main Category Found: %s | Url: %s", aria_label, url)
                    self.fetch_subcategory_links(url, aria_label, CATEGORY_LINKFARMS[aria_label])

        except Exception as e:
            logger.error(f"Error parsing sitemap: {e}")

    #fetch subcategory links
    def fetch_subcategory_links(self, url, category_name, linkfarm_ids):
        try:
            logger.info("Fetching subcategories for: %s", category_name)
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                selector = Selector(text=response.text)
                subcategory_urls = []
                
                for lf_id in linkfarm_ids:
                    # Construct XPath for specific linkfarm ID
                    xpath = f'//div[@id="comp_linkfarm_{lf_id}"]//li/a'
                    links = selector.xpath(xpath)
                    
                    for link in links:
                        subcategory_href = link.xpath('./@href').extract_first()
                        subcategory_name = link.xpath('./text()').extract_first()
                        
                        if subcategory_href:
                            full_link = f"https://www.jcpenney.com{subcategory_href}" 
                            subcategory_urls.append(full_link)
                            self.save_to_db(full_link, category_name, subcategory_name)
                            logger.info("  Found Subcategory: %s - %s", subcategory_name, full_link)
                logger.info("*" * 50)
                logger.info("Total subcategories for %s: %d", category_name, len(subcategory_urls))
            else:
                logger.error("Failed to fetch category page: %s Status: %s", url, response.status_code)
                
        except Exception as e:
            logger.error("Error fetching subcategories for %s: %s", category_name, e)

    #save to db
    def save_to_db(self, url, main_category, sub_category):
        try:
            document = {
                "main_category_name": main_category,
                "subcategory_name": sub_category,
                "url": url
            }
            self.collection.update_one(
                {"url": url},
                {"$set": document},
                upsert=True
            )
        except Exception as e:
            logger.error("Error saving document for %s: %s", url, e)
            


if __name__ == "__main__":
    crawler = Category()
    crawler.start()