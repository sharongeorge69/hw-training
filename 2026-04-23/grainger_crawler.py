import gzip
import io
import time
import random
import logging
import requests
import pymongo
from pymongo import MongoClient
from parsel import Selector

from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE,
    headers, cookies, SITEMAP_INDEX_URL
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GraingerCrawler:
    def __init__(self):
        self.headers = headers
        self.cookies = cookies
        
        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.col = self.db[MONGO_COLLECTION_RESPONSE]
        
        # Ensure unique index for de-duplication
        self.col.create_index("pdp_url", unique=True)
        logger.info(f"Connected to MongoDB: {MONGO_DB}")

    def fetch_url(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=60)
                
                if response.status_code == 200:
                    if url.endswith('.gz'):
                        # Handle compressed sitemaps
                        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                            return f.read().decode('utf-8')
                    return response.text
                else:
                    logger.error(f"    Failed [{response.status_code}] to fetch: {url}")
            
            except Exception as e:
                logger.warning(f"    Retryable error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                wait_time = random.uniform(2, 5)
                time.sleep(wait_time)
        return None

    def extract_urls_from_xml(self, xml_content):
        selector = Selector(text=xml_content, type='xml')
        return selector.xpath('//*[local-name()="loc"]/text()').getall()

    def parse_item(self, xml_content):
        """Extracts product URLs from a sitemap and saves them in bulk."""
        try:
            pdp_urls = self.extract_urls_from_xml(xml_content)
            # Filter for product detail URLs only
            product_urls = [url for url in pdp_urls if '/product/' in url]
            
            logger.info(f"    Extracted {len(product_urls)} product URLs.")
            
            items = [{"pdp_url": url} for url in product_urls]

            new_urls_count = 0
            if items:
                batch_size = 5000
                for i in range(0, len(items), batch_size):
                    batch = items[i : i + batch_size]
                    try:
                        result = self.col.insert_many(batch, ordered=False)
                        new_urls_count += len(result.inserted_ids)
                    except pymongo.errors.BulkWriteError as bwe:
                        new_urls_count += bwe.details.get('nInserted', 0)
                    except Exception as e:
                        logger.error(f"    Bulk insert error in batch: {e}")
            
            return new_urls_count
        except Exception as e:
            logger.error(f"    Error parsing XML content: {e}")
            return 0

    def start(self):
        logger.info(f"Starting Grainger Crawler from Index: {SITEMAP_INDEX_URL}")
        
        # 1. Fetch the Sitemap Index
        index_xml = self.fetch_url(SITEMAP_INDEX_URL)
        if not index_xml:
            logger.error("Could not fetch sitemap index. Aborting.")
            return

        sitemap_urls = self.extract_urls_from_xml(index_xml)
        
        # 2. Identify child sitemaps containing product items
        valid_sitemaps = [url for url in sitemap_urls if 'product-items-sitemap' in url]
        
        if not valid_sitemaps:
            logger.warning("No product-items-sitemaps found in index. Falling back to all sitemaps.")
            valid_sitemaps = [url for url in sitemap_urls if 'sitemap' in url]
        
        logger.info(f"Found {len(valid_sitemaps)} child sitemaps to process.")

        total_extracted = 0
        for idx, s_url in enumerate(valid_sitemaps, 1):
            logger.info(f"Processing Sitemap {idx}/{len(valid_sitemaps)}: {s_url}")
            
            xml_content = self.fetch_url(s_url)
            if not xml_content:
                logger.error(f"    Failed to retrieve sitemap contents: {s_url}")
                continue

            # 3. Process the sitemap and update count
            new_urls = self.parse_item(xml_content)
            total_extracted += new_urls
            
            logger.info(f"    Saved {new_urls} new URLs. (Total Session: {total_extracted})")

            # Politeness delay between sitemap files
            time.sleep(random.uniform(1.0, 3.0))

if __name__ == "__main__":
    crawler = GraingerCrawler()
    try:
        crawler.start()
    except KeyboardInterrupt:
        logger.info("Crawler stopped by user.")
    except Exception as e:
        logger.critical(f"Crawler crashed: {e}")
    finally:
        crawler.client.close()
