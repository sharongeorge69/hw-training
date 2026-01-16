import requests
from parsel import Selector
import json
import re
import time
import random
import json
import re
import time
import random
import logging
import csv
from urllib.parse import urljoin
from datetime import datetime
from pymongo import MongoClient

#   CONFIGURATION
BASE_URL = "https://www.marksandspencer.com"
MONGO_URI = "mongodb+srv://georgesharon2002_db_user:dyfKmcuKOP4r4iwM@cluster0.wb0ztdo.mongodb.net/?appName=Cluster0"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# How many PLP pages to crawl 
MAX_PLP_PAGES = 1

# Output file
OUTPUT_JSON = "marks_spencer_dresses.json"

#   SITEMAP DISCOVERY
def fetch_sitemap(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return Selector(text=r.text)
    except Exception as e:
        logging.error(f"Failed to fetch sitemap {url}: {e}")
        return None


def discover_dresses_plp():
    index_url = f"{BASE_URL}/sitemap/sitemap_index.xml"
    logging.info(f"→ Fetching sitemap index: {index_url}")

    index_sel = fetch_sitemap(index_url)
    if not index_sel:
        return None

    women_url = index_sel.xpath(
        "//loc[contains(text(), 'uk_sitemap_women.xml')]/text()"
    ).get()

    if not women_url:
        logging.warning("uk_sitemap_women.xml not found")
        return None

    logging.info(f"→ Found women sitemap: {women_url}")

    women_sel = fetch_sitemap(women_url)
    if not women_sel:
        return None

    dresses_url = women_sel.xpath(
        "//loc[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '/l/women/dresses')]/text()"
    ).get()

    if dresses_url:
        logging.info(f"→ Discovered dresses PLP: {dresses_url}")
        return dresses_url
    else:
        logging.warning("No /l/women/dresses found in women sitemap")
        return None


#   PLP → Collect PDP URLs
def scrape_plp(start_url, max_pages=MAX_PLP_PAGES):
    pdp_urls = set()
    current_url = start_url
    page = 1

    while current_url and page <= max_pages:
        logging.info(f"Scraping PLP page {page}: {current_url}")

        try:
            r = requests.get(current_url, headers=HEADERS, timeout=12)
            r.raise_for_status()
            sel = Selector(text=r.text)

            # Product links using your class name
            hrefs = sel.xpath('//a[contains(@class, "product-card_cardWrapper__GVSTY")]/@href').getall()

            added = 0
            for href in hrefs:
                full = urljoin(BASE_URL, href)
                full = re.sub(r'#.*$', '', full)
                if full not in pdp_urls:
                    pdp_urls.add(full)
                    added += 1

            logging.info(f"  → added {added} new products (total: {len(pdp_urls)})")

            # Pagination
            next_page = sel.xpath(
                '//a[contains(@class, "pagination_trigger__YEwyN") and contains(@aria-label, "Next")]/@href'
            ).get()

            if next_page:
                current_url = urljoin(BASE_URL, next_page)
                page += 1
                time.sleep(2.0 + random.uniform(0, 2.5))
            else:
                current_url = None
                logging.info("No more pages")

        except Exception as e:
            logging.error(f"PLP error on page {page}: {e}")
            break

    return list(pdp_urls)


#   PDP EXTRACTION (your logic)
def extract_pdp_fields(sel: Selector, pdp_url: str) -> dict:
    product = {
        "pdp_url": pdp_url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "unique_id": "N/A",
        "product_name": "N/A",
        "brand": "M&S",
        "category": "N/A",
        "regular_price": "N/A",
        "selling_price": "N/A",
        "promotion_description": "N/A",
        "breadcrumb": "N/A",
        "product_description": "N/A",
        "currency": "N/A",
        "color": "N/A",
        "size": "N/A",
        "rating": "N/A",
        "review": "N/A",
        "material_composition": "N/A",
        "style": "N/A",
        "care_instructions": "N/A",
        "images": "N/A",
        "composition": "N/A",
    }

    # 1. unique_id
    code_text = sel.xpath("substring-after(//p[contains(text(), 'Product code')], 'Product code: ')").get("")
    product["unique_id"] = code_text.strip() or re.search(r'/([a-z0-9]{8,})$', pdp_url, re.I).group(1) if not code_text else code_text

    # 2. product_name
    product["product_name"] = sel.xpath("//h1[@class='media-0_headingSm__aysOm']/text()").get("") or \
                              sel.xpath("//h1/text()").get("N/A").strip()

    # Breadcrumb + category
    bc_script = sel.xpath("//script[@type='application/ld+json' and contains(text(), 'BreadcrumbList')]/text()").get()
    if bc_script:
        try:
            bc = json.loads(bc_script)
            if bc.get('@type') == 'BreadcrumbList':
                items = bc.get('itemListElement', [])
                names = [i.get('item', {}).get('name', '').strip() for i in items if i.get('item')]
                product["breadcrumb"] = " > ".join(names)
                if names:
                    product["category"] = names[-1]
        except:
            pass

    # Price & Currency
    product["currency"] = "GBP"
    price_node = sel.xpath("//p[@class='media-0_headingSm__aysOm']/text()").get()
    
    if price_node:
        product["selling_price"] = re.sub(r'[^\d.]', '', price_node.strip())
        product["regular_price"] = product["selling_price"]
    
    # Description
    desc_node = sel.xpath("//p[contains(text(), 'About this style')]/following-sibling::p[1]/text()").get()
    product["product_description"] = desc_node.strip() if desc_node else "N/A"

    # Rating & Review 
    prod_script = sel.xpath("//script[@type='application/ld+json' and contains(text(), '\"@type\":\"Product\"')]/text()").get()
    if prod_script:
        try:
            json_prod = json.loads(prod_script)
            if json_prod and json_prod.get('@type') == 'Product':
                agg = json_prod.get('aggregateRating', {})
                product["rating"] = str(agg.get('ratingValue', "N/A"))
                product["review"] = str(agg.get('reviewCount', "N/A"))
        except:
            pass

    # Promotion_description
    if product["promotion_description"] == "N/A":
        promos = sel.xpath("//*[contains(@class, 'promotion') or contains(@class, 'offer') or contains(@class, 'badge')]/text()").getall()
        clean = [p.strip() for p in promos if p.strip()]
        if clean:
            product["promotion_description"] = " | ".join(clean)

    # Color
    if product["color"] == "N/A":
        color_node = sel.xpath("//span[contains(text(), 'Colour')]/following-sibling::span[contains(@class, 'media-0_textSm')]/text()").get()
        if color_node:
             product["color"] = color_node.strip()

    # Size
    sizes = sel.xpath("//div[contains(@class, 'selector-group-array_wrapper__yS98c')]//ul[contains(@class, 'selector-group-array_array__hAWxQ')]//li//span[not(contains(@class, 'visuallyHidden'))]/text()").getall()
    sizes = [s.strip() for s in sizes if s.strip() and "select" not in s.lower()]
    if not sizes:
        sizes = sel.xpath("//*[contains(text(),'Size')]/following::*[position()<=8]/text()").getall()
        sizes = [s.strip() for s in sizes if s.strip() and len(s.strip()) <= 8 and "size" not in s.lower()]
    product["size"] = ", ".join(sorted(set(sizes))) if sizes else "N/A"

    # Material / Composition
    comp = sel.xpath("//p[contains(text(), 'Composition')]/following-sibling::p[1]/text()").get()
    product["material_composition"] = comp.strip() if comp else "N/A"
    product["composition"] = product["material_composition"]

    # Style
    style_lines = sel.xpath("//p[contains(text(), 'Fit and style')]/following-sibling::div//p[not(contains(text(), '•'))]/text()").getall()
    style_clean = [s.strip() for s in style_lines if s.strip()]
    product["style"] = ", ".join(style_clean) if style_clean else product["category"]

    # Care
    care_lines = sel.xpath("//p[contains(text(), 'Care')]/following-sibling::div//p[contains(@class, 'product-details_careText__t_RPG')]/text()").getall()
    care_clean = [c.strip() for c in care_lines if c.strip()]
    product["care_instructions"] = ", ".join(care_clean) if care_clean else "N/A"

    # Images
    imgs = sel.xpath("//div[contains(@class, 'product-imagery_root')]//img/@src").getall()
    if not imgs:
        imgs = sel.xpath("//img[contains(@class, 'pdp') or contains(@class, 'product')]/@src").getall()
    clean_imgs = [urljoin(BASE_URL, src) for src in imgs if src and 'data:' not in src]
    product["images"] = ", ".join(dict.fromkeys(clean_imgs)) if clean_imgs else "N/A"   # deduplicate

    return product


#   DATA EXPORT & CONVERSION UTILITIES

def save_to_json_array(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved JSON Array: {filename}")
    except Exception as e:
        logging.error(f"Failed to save JSON Array: {e}")

def save_to_json_lines(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logging.info(f"Saved JSON Lines: {filename}")
    except Exception as e:
        logging.error(f"Failed to save JSON Lines: {e}")

def save_to_csv(data, filename, delimiter=','):
    if not data:
        return
    try:
        keys = set().union(*(d.keys() for d in data))
        fieldnames = sorted(list(keys))
        
        with open(filename, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Saved CSV ({'Pipe' if delimiter == '|' else 'Comma'}): {filename}")
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")

def convert_file_format(input_path, output_path, input_format='json', output_format='csv', delimiter=','):
    
    data = []
    try:
        # LOAD
        with open(input_path, 'r', encoding='utf-8') as f:
            if input_format == 'json':
                data = json.load(f)
            elif input_format == 'jsonl':
                data = [json.loads(line) for line in f]
            else:
                logging.error(f"Unsupported input format for conversion: {input_format}")
                return

        # SAVE
        if output_format == 'json':
            save_to_json_array(data, output_path)
        elif output_format == 'jsonl':
            save_to_json_lines(data, output_path)
        elif output_format == 'csv':
            save_to_csv(data, output_path, delimiter=delimiter)
        else:
            logging.error(f"Unsupported output format for conversion: {output_format}")

    except Exception as e:
        logging.error(f"Conversion failed: {e}")

#   MAIN
def main():
    plp_url = discover_dresses_plp()
    if not plp_url:
        logging.error("Could not find dresses PLP → stopping")
        return

    pdp_urls = scrape_plp(plp_url)

    if not pdp_urls:
        logging.warning("No products found")
        return

    results = []

    print("\n" + "="*70)
    print(f" Crawling {len(pdp_urls)} products...")
    print("="*70 + "\n")

    for i, url in enumerate(pdp_urls, 1):
        try:
            logging.info(f"[{i}/{len(pdp_urls)}] {url}")
            r = requests.get(url, headers=HEADERS, timeout=12)
            r.raise_for_status()
            sel = Selector(text=r.text)
            item = extract_pdp_fields(sel, url)
            results.append(item)
            time.sleep(1.8 + random.uniform(0, 2.2))
        except Exception as e:
            logging.error(f"Failed {url}: {e}")

    # --- SAVE TO MULTIPLE FORMATS ---
    base_name = "marks_spencer_dresses"
    
    # 1. JSON Array
    save_to_json_array(results, f"{base_name}.json")
    
    # 2. JSON Lines
    save_to_json_lines(results, f"{base_name}.jsonl")
    
    # 3. CSV (Normal)
    save_to_csv(results, f"{base_name}.csv", delimiter=',')
    
    # 4. CSV (Pipe Separated)
    save_to_csv(results, f"{base_name}_pipe.csv", delimiter='|')
    

    # Save to MongoDB
    if results:
        try:
            print("Connecting to MongoDB...")
            client = MongoClient(MONGO_URI)
            db = client["m_and_s_db"]
            collection = db["dresses"]
            
    
            inserted_count = 0
            for item in results:
                # Use unique_id as primary key if available, else pdp_url
                filter_query = {"unique_id": item["unique_id"]} if item["unique_id"] != "N/A" else {"pdp_url": item["pdp_url"]}
                
                result = collection.update_one(
                    filter_query,
                    {"$set": item},
                    upsert=True
                )
                if result.upserted_id or result.modified_count > 0:
                    inserted_count += 1
            
            print(f"Successfully synced {len(results)} products to MongoDB ({inserted_count} new/updated).")
            
        except Exception as e:
            logging.error(f"MongoDB Error: {e}")

    print(f"Example product name: {results[0].get('product_name', '—') if results else '—'}")


if __name__ == "__main__":
    main()