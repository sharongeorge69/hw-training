
import csv
import random
import time
import requests
from lxml import html

# Configuration
INPUT_CSV = "../styleunion_product_urls.csv"
# Scraping only Boys products urls
FILTER_PREFIX = "https://styleunion.in/products/boys-"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def extract_text(tree, xpaths):
    #Helper to extract text from a list of XPaths. Returns the first match.
    if isinstance(xpaths, str):
        xpaths = [xpaths]
    
    for xpath in xpaths:
        try:
            elements = tree.xpath(xpath)
            if elements:
                # If it's a list of strings (text nodes)
                if isinstance(elements[0], str):
                    return elements[0].strip()
                # If it's an element, try getting text_content()
                elif hasattr(elements[0], 'text_content'):
                    return elements[0].text_content().strip()
        except Exception:
            continue
    return "N/A"
#Parsing the url
def scrape_product(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        time.sleep(random.uniform(1, 2))
        
        tree = html.fromstring(response.content)
        
        data = {}
        data['url'] = url
        data['brand'] = "Style Union"
        data['country_of_origin'] = "India"
        
        # Title
        data['title'] = extract_text(tree, "//h1[contains(@class,'product__title')]")

        # Breadcrumbs
        if data['title'] != "N/A":
             data['breadcrumbs'] = f"home > {data['title']}"
        else:
             data['breadcrumbs'] = "home > N/A"

        # Regular & Selling Price
        price_xpaths = ["//span[contains(@class,'regular-price')]", 
                        "//div[contains(@class,'price__regular')]//span"]
        data['regular_price'] = extract_text(tree, price_xpaths)
        data['selling_price'] = extract_text(tree, price_xpaths)

        # SKU - Clean up "SKU: "
        raw_sku = extract_text(tree, ["//p[contains(@class,'product__sku')]//b", "//p[@id='sku-']//b"])
        data['sku'] = raw_sku.replace("SKU:", "").strip()
        
        # Description
        data['description'] = extract_text(tree, "//div[contains(@class,'accordion__content')]//div[contains(@class,'desc_inner')][2]//div[@class='acc__panel']")
        
        # Fit
        data['fit'] = extract_text(tree, ["//strong[contains(text(),'Fit')]/following-sibling::text()",
                                          "//b[contains(text(),'Fit')]/following-sibling::text()"])
        
        # Care Instruction
        data['care_instruction'] = extract_text(tree, "//h3[text()='Wash and Care']/following::div[@class='acc__panel'][1]")
        
        # Fabric Composition
        data['fabric_composition'] = extract_text(tree, ["//strong[contains(text(),'Fabric')]/following-sibling::text()",
                                                         "//b[contains(text(),'Fabric')]/following-sibling::text()"])

        # Dimensions (List of sizes)
        dimension_nodes = tree.xpath("//div[contains(@class, 'form__variants')]//span[@class='color__swatch-name']")
        if dimension_nodes:
            # Join with comma for CSV friendly format
            dims = [node.text_content().strip() for node in dimension_nodes]
            data['dimensions'] = ", ".join(dims)
        else:
            data['dimensions'] = ""

        # Net Quantity
        net_qty = tree.xpath("//input[contains(@class,'quantity__input')]/@value")
        if net_qty:
            data['net_quantity'] = net_qty[0]
        else:
            data['net_quantity'] = "1"

        return data
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
#Main function to scrape the product
def main():
    print("Starting Style Union 'Boys' Product Scraper...")
    
    target_urls = []
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row: continue
                url = row[0].strip()
                if url.startswith(FILTER_PREFIX):
                    target_urls.append(url)
    except FileNotFoundError:
        print(f"File {INPUT_CSV} not found.")
        return

    print(f"Found {len(target_urls)} matching URLs to scrape.")
    
    
    output_file = "styleunion_boys_products.csv"
    # Fieldnames in the order
    fieldnames = ['url', 'breadcrumbs', 'brand', 'title', 'regular_price', 'selling_price', 
                  'sku', 'description', 'dimensions', 'net_quantity', 'fit', 
                  'care_instruction', 'fabric_composition', 'country_of_origin']
    
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        #Count - To track how many products are scraped
        count = 0
        for url in target_urls:
            data = scrape_product(url)
            if data:
                writer.writerow(data)
                f.flush()
                count += 1
            
            if count % 10 == 0:
                print(f"Scraped {count}/{len(target_urls)}")

    print(f"\nScraping completed. Saved {count} records to {output_file}")

if __name__ == "__main__":
    main()
