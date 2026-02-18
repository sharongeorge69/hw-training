import requests
import json
import re
import logging
import html
import time
from mongoengine import connect, DynamicDocument
from jcpenney_items import ProductItem
import jcpenney_settings as settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class URLItem(DynamicDocument):
    meta = {'collection': settings.MONGO_COLLECTION_RESPONSE}

def parse_product_page(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.+?});', response.text)
        if not match:
            logger.warning(f"No PRELOADED_STATE for {url}")
            return None

        data = json.loads(match.group(1).replace("undefined", "null"))
        pd = data.get('productDetails', {})
        lots = pd.get('lots', [])
        
        # Brand & Description
        brand_data = pd.get('brand')
        brand = brand_data.get('name') if isinstance(brand_data, dict) else brand_data
        
        description = ""
        fit = ""
        colors = []
        sizes = set()

        if lots:
            lot = lots[0]
            raw_desc = lot.get('description', '')
            description = html.unescape(re.sub(r'<[^>]+>', '', raw_desc)).strip() if raw_desc else ""
            
            for attr in lot.get('bulletedAttributes', []):
                desc = attr.get('description', '')
                if desc.lower().startswith("fit:"):
                    fit = desc.split(':', 1)[1].strip()
                    break

            color_seq = pd.get('colorSequences') or lot.get('colorSequences', [])
            colors = [cs['color'] for cs in color_seq if 'color' in cs]

            for item in lot.get('items', []):
                for ov in item.get('optionValues', []):
                    if ov.get('name', '').lower() == 'size' and ov.get('value'):
                        sizes.add(ov.get('value').title())
                if item.get('size'):
                    sizes.add(item.get('size').title())

        if not description and pd.get('description'):
            description = html.unescape(re.sub(r'<[^>]+>', '', pd.get('description'))).strip()

        # Images & Valuation
        images = [img['url'] for img in pd.get('images', []) if isinstance(img, dict) and 'url' in img]
        valuation = pd.get('valuation', {})
        rating = valuation.get('rating')
        reviews = valuation.get('reviews', {}).get('count', 0) if valuation.get('reviews') else 0

        # Pricing API
        selling_price, regular_price, discount = "", "", ""
        if pd.get('id'):
            price_url = f"https://browse-api.jcpenney.com/v2/product-aggregator/{pd.get('id')}/additional-details?deliveryAvailabilityCheckRequired=false&GPA=false"
            try:
                api_headers = {**headers, 'Accept': 'application/json'}
                price_resp = requests.get(price_url, headers=api_headers, timeout=5)
                if price_resp.status_code == 200:
                    price_data = price_resp.json()
                    lot_price = price_data.get('lotPrice', {})
                    data_list = lot_price.get('data', [])
                    if data_list:
                        for amt in data_list[0].get('amounts', []):
                            if amt.get('minPercentOff'):
                                discount = amt.get('minPercentOff')
                            if amt.get('type') == 'ORIGINAL':
                                regular_price = amt.get('max')
                            elif amt.get('type') in ['SALE', 'CLEARANCE']:
                                selling_price = amt.get('max')
            except Exception as e:
                logger.error(f"Pricing error for {pd.get('id')}: {e}")

        return {
            "unique_id": str(pd.get('id', "")),
            "url": str(url),
            "product_name": str(pd.get('name', "")),
            "brand": str(brand) if brand else "",
            "selling_price": str(selling_price) if selling_price else "",
            "regular_price": str(regular_price) if regular_price else "",
            "discount": str(discount) if discount else "",
            "description": str(description),
            "specification": "",
            "fit_type": str(fit),
            "image": " , ".join(images),
            "rating": str(rating) if rating else "",
            "review": str(reviews),
            "size": " , ".join(sorted(list(sizes))),
            "colour": " , ".join(colors),
        }
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None

def process_products():
    try:
        connect(settings.MONGO_DB, host=settings.MONGO_URI)
        logger.info(f"Started processing. Collection: {settings.MONGO_COLLECTION_PRODUCTS}")
        
        total_docs = URLItem.objects.count()
        logger.info(f"Total URLs: {total_docs}")
        
        for idx, doc in enumerate(URLItem.objects.all(), 1):
            product_url = doc.product_url
            if not product_url: continue

            if ProductItem.objects(url=product_url).first():
                logger.debug(f"Skipped: {product_url}")
                continue
            
            logger.info(f"Item {idx}/{total_docs}: {product_url}")
            data = parse_product_page(product_url, settings.HEADERS)
            if data:
                try:
                    ProductItem(**data).save()
                except Exception as e:
                    logger.error(f"Save error: {e}")
            
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Batch error: {e}")

if __name__ == "__main__":
    process_products()
