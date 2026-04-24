import re
import json
import time
import random
import logging
import pymongo
from parsel import Selector
from pymongo import MongoClient

from settings import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_URL_FAILED, EXTRACTION_DATE, TARGET_URLS
)
from items import ProductDataItem
from msc_session_manager import MSCSessionManager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        # Session manager handles cookie refresh automatically
        session_mgr = MSCSessionManager()
        self.session, self.headers = session_mgr.get_session()

        # PyMongo connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]

        # Unique index on url
        self.product_collection.create_index("url", unique=True)
        logger.info("Connected to MongoDB")

    def clean_text(self, text):
        """Strip, collapse whitespace, remove non-printable chars."""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', ' ', text)          # strip HTML tags
        text = re.sub(r'[^\x20-\x7E]', ' ', text)     # remove non-ASCII
        return re.sub(r'\s+', ' ', text).strip()


    def fetch_page(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                logger.info(f"  Fetching: {url} (Attempt {attempt + 1})")
                resp = self.session.get(url, headers=self.headers, timeout=30)

                if resp.status_code == 200:
                    if "Pardon Our Interruption" in resp.text:
                        logger.warning("  Blocked by WAF refreshing session...")
                        from msc_session_manager import MSCSessionManager
                        mgr = MSCSessionManager()
                        self.session, self.headers = mgr._refresh_via_browser.__func__(mgr) or (self.session, self.headers)
                        continue
                    return resp.text

                elif resp.status_code == 404:
                    logger.error(f"  Product not found (404): {url}")
                    return None
                else:
                    logger.error(f"  Failed [{resp.status_code}]: {url}")

            except Exception as e:
                logger.warning(f"  Error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                wait = 2 ** attempt + random.uniform(0, 1)
                logger.info(f"  Retrying in {wait:.1f}s...")
                time.sleep(wait)

        return None

    def parse_item(self, pdp_url, html_content):
        try:
            sel = Selector(text=html_content)

            # JSON-LD
            ld_data = {}
            for raw in sel.xpath('//script[@type="application/ld+json"]/text()').extract():
                try:
                    d = json.loads(raw)
                    if d.get("@type") == "Product":
                        ld_data = d
                        break
                except Exception:
                    continue

            offers = ld_data.get("offers", {})

            brand_name = ld_data.get("brand", {}).get("name", "")
            manufacturer_name = brand_name
            item_name = self.clean_text(ld_data.get("name", ""))
            full_description = self.clean_text(ld_data.get("description", ""))
            manufacturer_part_number = ld_data.get("mpn", "")
            vendor_part_number = ld_data.get("sku", "")
            price = str(offers.get("price", ""))
            availability = offers.get("availability", "")
            url_field = ld_data.get("url", pdp_url)

            # Country of Origin 
            country_of_origin = self.clean_text(
                sel.xpath(
                    '//td[.//span[contains(text(), "Country of Origin")]]'
                    '/text()[normalize-space()]'
                ).extract_first("").strip()
            )

            # Unit of Issue & QTY per UOI 
            # unit_of_issue = ""
            # qty_per_uoi   = ""
            # qty_raw = sel.xpath(
            #     '//*[re:test(text(), "Order Qty of \\d+ equals", "i")]/text()',
            #     namespaces={"re": "http://exslt.org/regular-expressions"}
            # ).extract_first("")
            # if qty_raw:
            #     m = re.search(r"equals\s*\(\d+\)\s*(\d+)\s*([A-Za-z]+)", qty_raw)
            #     if m:
            #         qty_per_uoi   = m.group(1)
            #         unit_of_issue = m.group(2)

            # Product Category (breadcrumb) 
            bc_links = sel.xpath('//div[@id="pdp-breadcrumb"]//ol/li/a/text()').extract()
            product_category = " > ".join(t.strip() for t in bc_links if t.strip())

            upc           = ""
            model_number  = ""
            rohs_reach    = ""
            lead_time     = ""
            stock_on_hand = ""

            # Extract specs table into full_product_description_2 dictionary
            spec_dict = {}
            specs = sel.xpath('//div[@id="specs-table-wrapper"]//td[@id and @data-value]')
            for td in specs:
                k = td.xpath('./@id').extract_first("").strip()
                v = td.xpath('./@data-value').extract_first("").strip()
                if k and v:
                    spec_dict[k] = v

            item = {}
            item["company_name"] = "MSCDirect"
            item["manufacturer_name"] = manufacturer_name
            item["brand_name"] = brand_name
            item["manufacturer_part_number"] = manufacturer_part_number
            item["vendor_seller_part_number"] = vendor_part_number
            item["item_name"] = item_name
            item["full_product_description"] = full_description
            item["price"] = price
            item["country_of_origin"] = country_of_origin
            item["unit_of_issue"] = ""
            item["qty_per_uoi"] = ""
            item["upc"] = upc
            item["model_number"] = model_number
            item["product_category"] = product_category
            item["url"] = url_field
            item["availability"] = availability
            item["date_crawled"] = EXTRACTION_DATE
            item["lead_time"] = lead_time
            item["rohs_reach"] = rohs_reach
            item["stock_on_hand"] = stock_on_hand
            item["full_product_description_2"] = spec_dict


            # Save to MongoDB
            try:
                ProductDataItem(**item).validate()
                self.product_collection.insert_one(item)
                logger.info(f"  Saved: {item['item_name']} ({pdp_url})")
            except pymongo.errors.DuplicateKeyError:
                logger.info(f"  Already exists (skipping): {pdp_url}")
            except Exception as e:
                logger.error(f"  Save error for {pdp_url}: {e}")

        except Exception as e:
            logger.error(f"  Error parsing {pdp_url}: {e}", exc_info=True)


    def start(self):
        total = len(TARGET_URLS)
        logger.info(f"Starting MSC Direct parser — {total} URLs to process")

        for idx, url in enumerate(TARGET_URLS, 1):
            logger.info(f"\nProcessing {idx}/{total}: {url}")

            html = self.fetch_page(url)
            if not html:
                logger.error(f"  Failed to fetch — logging to failed collection.")
                self.failed_url_collection.update_one(
                    {"url": url},
                    {"$set": {"url": url, "date_crawled": EXTRACTION_DATE}},
                    upsert=True
                )
                continue

            self.parse_item(url, html)
            time.sleep(random.uniform(1.0, 2.5))

    def close(self):
        try:
            self.client.close()
            logger.info("MongoDB connection closed.")
        except Exception:
            pass


if __name__ == "__main__":
    parser_obj = Parser()
    try:
        parser_obj.start()
    except Exception as e:
        logger.critical(f"Parser crashed: {e}", exc_info=True)
    finally:
        parser_obj.close()
