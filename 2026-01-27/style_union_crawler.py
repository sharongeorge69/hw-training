import style_union_settings as settings
import requests
from parsel import Selector
import logging
import pymongo
from datetime import datetime
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StyleUnionCrawler:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.headers = settings.HEADERS
        
        # MongoDB connection
        self.mongo_uri = settings.MONGO_URI
        self.db_name = settings.DB_NAME
        self.category_collection_name = settings.COLLECTION_CATEGORY
        self.product_collection_name = settings.COLLECTION_PRODUCT_URLS
        
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.category_collection = self.db[self.category_collection_name]
            self.product_collection = self.db[self.product_collection_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_pending_categories(self):
        try:
            categories = list(self.category_collection.find({}, {"url": 1}))
            logger.info(f"Found {len(categories)} categories to crawl")
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def crawl_category(self, category_url):
        all_product_urls = []
        current_url = category_url
        page_count = 1
        
        try:
            while current_url:
                logger.info(f"Crawling category: {current_url} (Page {page_count})")
                response = requests.get(current_url, headers=self.headers, timeout=settings.TIMEOUT)
                response.raise_for_status()
                
                sel = Selector(text=response.text)
                
                # Extract product links on current page
                # Targeted XPath to avoid "You may also like" or "Recently viewed" sections
                product_links = set(sel.xpath('//div[contains(@id, "ProductGridContainer")]//a[contains(@href, "/products/")]/@href').getall())
                
                # Process links
                for link in product_links:
                    full_url = urljoin(self.base_url, link)
                    if "/products/" in full_url:
                        # Normalize URL: strip /collections/... prefix if present
                        prod_idx = full_url.find("/products/")
                        if prod_idx != -1:
                            # Keep scheme+netloc+normalized_path
                            # Simple string manipulation since base_url is known
                            path_and_query = full_url[prod_idx:]
                            full_url = "https://styleunion.in" + path_and_query
                        
                        all_product_urls.append(full_url)
                

                next_page_path = sel.xpath('//infinite-scroll/@data-url').get()
                if next_page_path:
                    # The data-url is often relative like "/collections/...?page=2"
                    current_url = urljoin(self.base_url, next_page_path)
                    page_count += 1
                    # Safety break to prevent infinite loops if logic fails
                    if page_count > 50: 
                        logger.warning(f"Reached safety page limit for {category_url}")
                        break
                else:
                    current_url = None

            unique_urls = list(set(all_product_urls))
            logger.info(f"Found {len(unique_urls)} unique products in {category_url} across {page_count} pages")
            return unique_urls

        except requests.RequestException as e:
            logger.error(f"Error crawling {current_url}: {e}")
            # Return whatever we found so far
            return list(set(all_product_urls))

    def save_product_urls(self, product_urls, category_url):
        if not product_urls:
            return

        added_count = 0
        for url in product_urls:
            try:
                result = self.product_collection.update_one(
                    {"url": url},
                    {
                        "$set": {
                            "source_category": category_url
                        },
                        "$setOnInsert": {
                            "url": url,
                            "created_at": datetime.now()
                        }
                    },
                    upsert=True
                )
                if result.upserted_id:
                    added_count += 1
            except Exception as e:
                logger.error(f"Error saving product URL {url}: {e}")
        
        logger.info(f"Saved {len(product_urls)} products from {category_url} ({added_count} new)")

    def run(self):
        categories = self.get_pending_categories()
        for cat in categories:
            url = cat.get('url')
            if url:
                start_time = datetime.now()
                product_urls = self.crawl_category(url)
                self.save_product_urls(product_urls, url)

if __name__ == "__main__":
    crawler = StyleUnionCrawler()
    crawler.run()
