import requests
from parsel import Selector
from lxml import etree
import re
from datetime import datetime
import logging
from pymongo import MongoClient
import json
import csv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_sitemap():
    """Scrape sitemap data using lxml to find dresses PLP URL."""
    try:
        response = requests.get('https://www.marksandspencer.com/sitemap/sitemap_index.xml', headers=headers)
        response.raise_for_status()
        tree = etree.fromstring(response.content)
        namespaces = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = tree.xpath('//s:loc', namespaces=namespaces)
        
        # Find women sitemap
        women_sitemap = next((loc.text for loc in locs if 'uk_sitemap_women.xml' in loc.text), None)
        if not women_sitemap:
            logging.warning("Women sitemap not found.")
            return None
        
        # Fetch women sitemap
        resp = requests.get(women_sitemap, headers=headers)
        resp.raise_for_status()
        tree = etree.fromstring(resp.content)
        cat_locs = tree.xpath('//s:loc', namespaces=namespaces)
        
        # Find dresses category URL
        dresses_plp = next((loc.text for loc in cat_locs if '/dresses' in loc.text), None)
        if dresses_plp:
            logging.info(f"Found dresses PLP: {dresses_plp}")
            return dresses_plp
        else:
            logging.warning("Dresses PLP not found in sitemap.")
            return None
    except requests.RequestException as e:
        logging.error(f"Request error in sitemap scraping: {e}")
    except etree.XMLSyntaxError as e:
        logging.error(f"XML parsing error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in sitemap scraping: {e}")
    return None

def scrape_plp(plp_url):
    """Scrape PLP for PDP URLs, pagination, category name, etc."""
    data = []
    while plp_url:
        try:
            resp = requests.get(plp_url, headers=headers)
            resp.raise_for_status()
            sel = Selector(text=resp.text)
            
            # Extract category name (adjust XPath based on actual structure)
            category = sel.xpath('//h1[@class="category-title"]/text()').get() or sel.xpath('//title/text()').get()
            if category:
                category = category.strip()
            logging.info(f"Scraping PLP: {plp_url} | Category: {category}")
            
            # Extract PDP URLs (adjust XPath)
            pdp_urls = sel.xpath('//div[contains(@class, "product-item")]//a/@href').getall()
            for url in pdp_urls:
                if not url.startswith('https://'):
                    url = 'https://www.marksandspencer.com' + url
                product_data = scrape_pdp(url)
                if product_data:
                    product_data['category'] = category
                    product_data['timestamp'] = datetime.now().isoformat()
                    data.append(product_data)
            
            # Pagination (adjust XPath)
            next_page = sel.xpath('//a[@rel="next"]/@href').get()
            if next_page:
                if not next_page.startswith('https://'):
                    next_page = 'https://www.marksandspencer.com' + next_page
                plp_url = next_page
            else:
                plp_url = None
        except requests.RequestException as e:
            logging.error(f"Request error in PLP: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error in PLP: {e}")
            break
    return data

def scrape_pdp(pdp_url):
    """Scrape PDP for specified fields using XPath and regex fallback."""
    try:
        resp = requests.get(pdp_url, headers=headers)
        resp.raise_for_status()
        sel = Selector(text=resp.text)
        text = resp.text  # For regex fallback
        
        # XPath extractions (adjust based on actual site inspection)
        product_name = sel.xpath('//h1[contains(@class, "product-name")]/text()').get()
        brand = sel.xpath('//span[@itemprop="brand"]/text()').get() or 'Marks & Spencer'
        regular_price = sel.xpath('//span[contains(@class, "regular-price")]/text()').get()
        selling_price = sel.xpath('//span[contains(@class, "sale-price")]/text()').get()
        promotion_description = sel.xpath('//div[contains(@class, "promotion")]/text()').get()
        breadcrumb = ' > '.join(sel.xpath('//nav[@aria-label="breadcrumb"]//a/text()').getall()).strip()
        product_description = ' '.join(sel.xpath('//div[contains(@id, "description")]//p/text()').getall()).strip()
        currency = sel.xpath('//meta[@itemprop="priceCurrency"]/@content').get() or 'GBP'
        color = sel.xpath('//ul[contains(@class, "colors")]//li/text()').getall()
        size = sel.xpath('//select[contains(@class, "sizes")]//option/text()').getall()
        rating = sel.xpath('//span[@itemprop="ratingValue"]/text()').get()
        review = sel.xpath('//span[@itemprop="reviewCount"]/text()').get()
        material_composition = sel.xpath('//div[contains(@class, "composition")]/text()').get()
        style = sel.xpath('//div[contains(@class, "style")]/text()').get()
        care_instructions = sel.xpath('//div[contains(@class, "care-instructions")]/text()').get()
        feature = ' '.join(sel.xpath('//ul[contains(@class, "features")]//li/text()').getall()).strip()
        images = sel.xpath('//img[contains(@class, "product-image")]/@src').getall()
        composition = material_composition  # Often same as material_composition
        
        # Unique ID from URL using regex
        unique_id_match = re.search(r'/p/([a-zA-Z0-9]+)', pdp_url)
        unique_id = unique_id_match.group(1) if unique_id_match else ''
        
        # Regex fallbacks for dress-related fields if XPath fails (examples)
        if not regular_price:
            regular_price_match = re.search(r'Regular price:\s*(\£\d+(?:\.\d+)?)', text, re.IGNORECASE)
            regular_price = regular_price_match.group(1) if regular_price_match else ''
        if not selling_price:
            selling_price_match = re.search(r'Now:\s*(\£\d+(?:\.\d+)?)', text, re.IGNORECASE)
            selling_price = selling_price_match.group(1) if selling_price_match else ''
        if not material_composition:
            material_match = re.search(r'Material:\s*(.*?)(\n|$)', text, re.IGNORECASE)
            material_composition = material_match.group(1).strip() if material_match else ''
        
        # Serialize lists to strings
        color_str = ', '.join(color)
        size_str = ', '.join(size)
        images_str = ', '.join(images)
        
        data = {
            'unique_id': unique_id,
            'product_name': product_name.strip() if product_name else '',
            'brand': brand.strip() if brand else '',
            'category': '',  # Filled in PLP
            'regular_price': regular_price.strip() if regular_price else '',
            'selling_price': selling_price.strip() if selling_price else '',
            'promotion_description': promotion_description.strip() if promotion_description else '',
            'breadcrumb': breadcrumb,
            'pdp_url': pdp_url,
            'product_description': product_description,
            'currency': currency,
            'color': color_str,
            'size': size_str,
            'rating': rating.strip() if rating else '',
            'review': review.strip() if review else '',
            'material_composition': material_composition.strip() if material_composition else '',
            'style': style.strip() if style else '',
            'care_instructions': care_instructions.strip() if care_instructions else '',
            'feature': feature,
            'images': images_str,
            'composition': composition.strip() if composition else ''
        }
        return data
    except requests.RequestException as e:
        logging.error(f"Request error in PDP {pdp_url}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in PDP {pdp_url}: {e}")
    return None

def insert_to_db(data):
    """Insert data into MongoDB."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['marks_spencer_db']
        collection = db['products']
        if data:
            collection.insert_many(data)
            logging.info(f"Inserted {len(data)} products into MongoDB.")
    except Exception as e:
        logging.error(f"Error inserting to DB: {e}")

def export_data(data):
    """Export data to various formats."""
    if not data:
        logging.warning("No data to export.")
        return
    
    # JSON Array
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    logging.info("Exported to products.json (JSON Array)")
    
    # JSON Lines
    with open('products.jsonl', 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    logging.info("Exported to products.jsonl (JSON Lines)")
    
    # Normal CSV
    with open('products.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logging.info("Exported to products.csv (Comma-separated CSV)")
    
    # Pipe-Separated CSV
    with open('products_pipe.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter='|')
        writer.writeheader()
        writer.writerows(data)
    logging.info("Exported to products_pipe.csv (Pipe-separated CSV)")

def convert_formats():
    """Convert one data format to another (e.g., JSON to CSV)."""
    try:
        # Read JSON Array
        with open('products.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert to CSV
        with open('converted_from_json.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=json_data[0].keys())
            writer.writeheader()
            writer.writerows(json_data)
        logging.info("Converted products.json to converted_from_json.csv")
    except FileNotFoundError as e:
        logging.error(f"File not found for conversion: {e}")
    except Exception as e:
        logging.error(f"Error in format conversion: {e}")

# Main execution
if __name__ == "__main__":
    plp_url = scrape_sitemap() or 'https://www.marksandspencer.com/l/women/dresses'  # Fallback to known PLP
    data = scrape_plp(plp_url)
    insert_to_db(data)
    export_data(data)
    convert_formats()