import requests
from parsel import Selector
from urllib.parse import urlparse, parse_qs
import logging
import jcpenney_settings as settings
from mongoengine import connect, DynamicDocument

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CategoryDoc(DynamicDocument):
    meta = {
        'collection': settings.MONGO_COLLECTION_CATEGORY,
        'indexes': [{'fields': ['url'], 'unique': True}]
    }

class CategorySitemap:
    def __init__(self):
        connect(settings.MONGO_DB, host=settings.MONGO_URI)
        self.headers = settings.HEADERS
        
    def start(self):
        try:
            resp = requests.get(settings.SITEMAP_URL, headers=self.headers, timeout=10)
            resp.raise_for_status()
            self.parse_sitemap(resp.text)
        except Exception as e:
            logger.error(f"Sitemap error: {e}")

    def parse_sitemap(self, html_content):
        selector = Selector(text=html_content)
        linkfarms = {
            "Women": ["2", "4"],
            "Men": ["2", "3"],
            "Juniors": ["1", "5"],
            "Kids": ["1", "2"],
            "Jewelry & Watches": ["1", "2", "3", "5"],
            "Handbags": ["0", "1"]
        }
        
        for node in selector.xpath('//a[@class="deptLink PTZFD"]'):
            label = node.xpath('./@aria-label').get()
            href = node.xpath('./@href').get()
            
            if label in linkfarms and href:
                url = f"https://www.jcpenney.com{href}"
                logger.info(f"Main Category: {label}")
                self.fetch_subcategories(url, label, linkfarms[label])

    def fetch_subcategories(self, url, main_cat, linkfarm_ids):
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code != 200: return
            
            sel = Selector(text=resp.text)
            for lf_id in linkfarm_ids:
                for link in sel.xpath(f'//div[@id="comp_linkfarm_{lf_id}"]//li/a'):
                    href = link.xpath('./@href').get()
                    name = link.xpath('./text()').get()
                    
                    if href and name:
                        full_url = f"https://www.jcpenney.com{href}"
                        self.save_category(full_url, main_cat, name.strip())
                        logger.info(f"  Subcategory Found: {name.strip()}")
        except Exception as e:
            logger.error(f"Error fetching subcategories for {main_cat}: {e}")

    def save_category(self, url, main_cat, sub_cat):
        try:
            parsed = urlparse(url)
            cat_id = parse_qs(parsed.query).get("id", [None])[0]
            api_url = f"https://search-api.jcpenney.com/v1/search-service{parsed.path}?id={cat_id}&responseType=organic" if cat_id else None

            CategoryDoc.objects(url=url).update_one(
                set__main_category_name=main_cat,
                set__subcategory_name=sub_cat,
                set__category_id=cat_id,
                set__api_url=api_url,
                upsert=True
            )
        except Exception as e:
            logger.error(f"Save error for {url}: {e}")

if __name__ == "__main__":
    CategorySitemap().start()