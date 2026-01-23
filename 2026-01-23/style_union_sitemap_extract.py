
import requests
import xml.etree.ElementTree as ET
import csv
import time
import random

SITEMAP_URL = "https://styleunion.in/sitemap.xml"
OUTPUT_FILE = "styleunion_product_urls.csv"

# Mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Namespace usually found in sitemaps
NAMESPACES = {
    'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
}

def fetch_xml(url):
    """Fetches the XML content from a URL."""
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        # Basic sleep to be polite
        time.sleep(random.uniform(0.5, 1.5))
        return ET.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML from {url}: {e}")
        return None

def process_sitemap(url, product_urls):
    """Recursively processes a sitemap URL."""
    root = fetch_xml(url)
    if root is None:
        return

    # Check if it's a sitemap index (contains other sitemaps)
    # Finding 'sitemap' tags
    sitemaps = root.findall('ns:sitemap', NAMESPACES)
    if sitemaps:
        print(f"Found {len(sitemaps)} sub-sitemaps in {url}")
        for sitemap in sitemaps:
            loc = sitemap.find('ns:loc', NAMESPACES)
            if loc is not None and loc.text:
                process_sitemap(loc.text.strip(), product_urls)
    
    # Check if it's a urlset (contains actual URLs)
    urls = root.findall('ns:url', NAMESPACES)
    if urls:
        print(f"Found {len(urls)} URLs in {url}")
        for url_tag in urls:
            loc = url_tag.find('ns:loc', NAMESPACES)
            if loc is not None and loc.text:
                url_str = loc.text.strip()
                
                # Apply filters
                if "/products/" in url_str:
                    if not (url_str.endswith("-remote") or url_str.endswith("-remote/")):
                         product_urls.add(url_str)

def main():
    print("Starting Style Union Sitemap Scraper...")
    product_urls = set()
    
    process_sitemap(SITEMAP_URL, product_urls)
    
    sorted_urls = sorted(list(product_urls))
    total_count = len(sorted_urls)
    
    print(f"\nTotal product URLs found: {total_count}")
    
    if total_count > 0:
        print("\nFirst 10 URLs:")
        for u in sorted_urls[:10]:
            print(u)
            
        print("\nLast 10 URLs:")
        for u in sorted_urls[-10:]:
            print(u)
            
        # Save to CSV
        try:
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # writer.writerow(["Product URL"]) # Header optional based on prompt "one URL per line", but usually good. 
                # Prompt said "one URL per line", listing sample implies bare list, but CSV usually implies header or comma separated.
                # However "one URL per line" in a file usually suggests a plain text file or a single column CSV.
                # I'll stick to single column, no header to strictly follow "one URL per line" as simple list often preferred
                # but "CSV" implies it might open in Excel. I'll just write the URL.
                for u in sorted_urls:
                    writer.writerow([u])
            print(f"\nSuccessfully saved URLs to {OUTPUT_FILE}")
        except IOError as e:
            print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
