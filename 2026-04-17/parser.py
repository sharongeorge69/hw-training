import time
import json
import re
from datetime import datetime
from camoufox.sync_api import Camoufox
from parsel import Selector

def extract_data(url):
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        # Navigate to a URL
        print(f"Navigating to {url}...")
        
        # Camoufox handles bypass automatically
        response = page.goto(url, wait_until="load", timeout=60000)
        
        if not response or response.status != 200:
            print(f"Error: Failed to fetch page. Status: {response.status if response else 'No Response'}")
            return None

        # Wait for dynamic content
        time.sleep(1)
        
        html = page.content()
        selector = Selector(text=html)
        
        # 1. JSON-LD Extraction for core catalog data
        json_ld_data = {}
        json_ld_scripts = selector.xpath('//script[@type="application/ld+json"]/text()').getall()
        for script in json_ld_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "Product":
                            json_ld_data = item
                elif data.get("@type") == "Product":
                    json_ld_data = data
            except:
                continue

        # 2. Field Mapping & Extraction
        
        # Item Name
        item_name = selector.css('h1.product__title::text').get() or json_ld_data.get('name', '')
        item_name = item_name.strip() if item_name else ""

        # Manufacturer / Brand
        brand_name = selector.css('.product-vendor a::text').get() or json_ld_data.get('brand', {}).get('name', '')
        brand_name = brand_name.strip() if brand_name else ""
        manufacturer_name = brand_name

        # MPN / SKU
        sku = json_ld_data.get('sku', '')
        if not sku:
            sku_text = selector.css('.product__sku::text').get()
            sku = sku_text.strip() if sku_text else ""
        
        # MPN often matches SKU or is listed near ITEM #
        mpn = sku
        item_num_text = selector.xpath('//*[contains(text(), "ITEM #")]/text()').get()
        if item_num_text:
            match = re.search(r'ITEM #:\s*(\w+)', item_num_text)
            if match:
                mpn = match.group(1)

        # Price
        price_text = selector.css('.price__current::text').get()
        if not price_text:
            price_val = json_ld_data.get('offers', [{}])[0].get('price', '')
            price = str(price_val)
        else:
            # Clean price string
            price = re.sub(r'[^\d.]', '', price_text.strip())

        # Description (look for first accordion or JSON-LD)
        description = selector.css('.accordion__content::text').get() or json_ld_data.get('description', '')
        description = ' '.join(description.split()) if description else ""

        # Breadcrumbs / Category
        categories = selector.css('.breadcrumbs__link::text').getall()
        if not categories or len(categories) <= 1:
            # Fallback to web-pixels JSON
            pixel_match = re.search(r'"type":"([^"]+)"', html)
            if pixel_match:
                type_str = pixel_match.group(1)
                categories = [c.strip() for c in type_str.replace('&gt;', '>').split('>') if c.strip()]
        
        categories = [c.strip() for c in categories if c.strip().lower() not in ['home', '/']]
        product_category = " > ".join(categories)

        # Availability
        inventory_notice = selector.css('.product-form__inventory-notice::text').get() or ""
        availability_ld = json_ld_data.get('offers', [{}])[0].get('availability', '')
        
        if "InStock" in availability_ld or "In Stock" in inventory_notice:
            availability = "In Stock"
        else:
            availability = "Out of Stock"
        
        # Stock on Hand
        stock_on_hand = ""
        inventory_script = selector.css('script[data-product-inventory-json]::text').get()
        if inventory_script:
            try:
                inventory_data = json.loads(inventory_script)
                # Shopify inventory JSON is usually keyed by variant ID
                inventory_items = inventory_data.get('inventory', {})
                if inventory_items:
                    # Get the first variant's inventory quantity
                    first_variant = list(inventory_items.values())[0]
                    stock_on_hand = str(first_variant.get('inventory_quantity', ''))
            except Exception as e:
                print(f"Error parsing inventory JSON: {e}")

        # If not found in script, fallback to regex on raw HTML
        if not stock_on_hand:
            stock_match = re.search(r'"inventory_quantity":(\d+)', html)
            if stock_match:
                stock_on_hand = stock_match.group(1)
                
        # Lead Time
        lead_time = ""
        lead_time_tag = selector.css('.product-blocks__shipping-info::text').get() or ""
        if not lead_time_tag:
            # Look for common Shopify shipping text patterns
            time_match = re.search(r'Ships in\s*([\w\s-]+)', html)
            if time_match:
                lead_time = time_match.group(1).strip()
        else:
            lead_time = lead_time_tag.strip()

        # UPC
        upc = ""
        # Often UPCs are 12 digits
        upc_match = re.search(r'(?:UPC|GTIN):\s*(\d{12,13})', html)
        if not upc_match:
            upc_match = re.search(r'"gtin12":"(\d+)"', html) # Check JSON blocks
        if upc_match:
            upc = upc_match.group(1)

        # Country of Origin
        country_of_origin = ""
        co_match = re.search(r'(?:Country of Origin|Origin):\s*([A-Za-z\s]+)', html, re.IGNORECASE)
        # Filters known layout garbage
        if co_match:
            val = co_match.group(1).strip()
            if len(val) < 30 and not any(x in val.lower() for x in ['center', 'top', 'width']):
                country_of_origin = val

        # Model Number
        model_number = ""
        model_match = re.search(r'Model\s*([\w\d-]+)', item_name + " " + description)
        if model_match:
            model_number = model_match.group(1)

        # Compliance (RoHS/Reach)
        rohs_reach = ""
        compliance_flags = []
        if "RoHS" in html: compliance_flags.append("RoHS")
        if "REACH" in html.upper(): compliance_flags.append("REACH")
        rohs_reach = ", ".join(compliance_flags)

        # UOI / Qty Per UOI
        uoi = "Each"
        qty_per_uoi = "1"
        uoi_text = selector.xpath('//*[contains(@class, "price")]/following-sibling::*[contains(text(), "/")]/text()').get()
        if uoi_text:
            uoi = uoi_text.replace('/', '').strip()

        # Final Dataset
        extracted_fields = {
            "Manufacturer Name": manufacturer_name,
            "Brand Name": brand_name,
            "Manufacturer Part Number (Product Item Number)": mpn,
            "Vendor Seller Part Number": sku,
            "Item Name": item_name,
            "Full Product Description": description[:500] + "..." if len(description) > 500 else description,
            "Price": price,
            "Country of Origin": country_of_origin,
            "Unit of Issue (UOI)": uoi,
            "QTY Per UOI": qty_per_uoi,
            "UPC": upc,
            "Model Number": model_number,
            "Product Category": product_category,
            "URL": url,
            "Availability": availability,
            "Date Crawled": datetime.now().strftime("%Y-%m-%d"),
            "Lead Time": lead_time,
            "RoHs/Reach": rohs_reach,
            "Stock on Hand": stock_on_hand
        }
        
        return extracted_fields

if __name__ == "__main__":
    test_url = "https://www.restockit.com/products/3m-peltor-x-series-earmuffs-num-mmmx5a"
    data = extract_data(test_url)
    if data:
        print("\nExtracted Product Data:")
        print(json.dumps(data, indent=4))
