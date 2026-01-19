import requests
import lxml.html
import csv
import json
import re
import time
from urllib.parse import urljoin

class BayutScraper:
    def __init__(self):
        self.base_url = "https://www.bayut.bh/en/to-rent/commercial/bahrain/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.data_list = []
        
        # Fields matches the scrapy Item definition
        self.fields = [
            "reference_number", "id", "url", "purpose", "title", "description",
            "location", "price", "currency", "price_per", "furnished",
            "amenities", "details", "agent_name", "number_of_photos",
            "breadcrumb", "property_image_urls", "property_type"
        ]

    def get_dom(self, url):
        """Fetches the URL and returns an lxml DOM object."""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return lxml.html.fromstring(response.content)
            else:
                print(f"Failed to fetch {url}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_property(self, url, tree):
        """Extracts property details using XPaths directly."""
        item = {}
        
        # url
        item["url"] = url
        
        # id
        m = re.search(r"details-(\d+)", url)
        item["id"] = m.group(1) if m else None
        
        # reference_number
        ref_list = tree.xpath("//span[contains(text(),'Bayut')]/text()")
        item["reference_number"] = ref_list[0].strip() if ref_list else None
        
        # purpose
        item["purpose"] = "For Rent"
        
        # currency
        item["currency"] = "BHD"
        
        # title
        title_list = tree.xpath("//h1/text()")
        item["title"] = title_list[0].strip() if title_list else None
        
        # description
        desc_list = tree.xpath("//div[@aria-label='Property description']//text()")
        item["description"] = " ".join([d.strip() for d in desc_list if d.strip()])
        
        # location
        loc_list = tree.xpath("//div[@aria-label='Property header']/text()")
        item["location"] = loc_list[0].strip() if loc_list else None
        
        # price
        price_list = tree.xpath("//span[@aria-label='Price']/text()")
        item["price"] = price_list[0].strip() if price_list else None
        
        # price_per
        pper_list = tree.xpath("//span[@aria-label='Frequency']/text()")
        item["price_per"] = pper_list[0].strip() if pper_list else None
        
        # furnished
        furn_list = tree.xpath("//span[@aria-label='Furnishing']/text()")
        item["furnished"] = furn_list[0].strip() if furn_list else None
        
        # amenities
        item["amenities"] = tree.xpath("//div[contains(@class,'dd50d995')]//span/text()")
        
        # details
        det_list = tree.xpath("//span[@aria-label='Area']//span/text()")
        item["details"] = det_list[0].strip() if det_list else None
        
        # agent_name
        agent_list = tree.xpath("//span[@aria-label='Agent name']/text()")
        item["agent_name"] = agent_list[0].strip() if agent_list else None
        
        # breadcrumb
        item["breadcrumb"] = [x.strip() for x in tree.xpath("//div[@aria-label='Breadcrumb']//text()") if x.strip()]
        
        # property_image_urls
        item["property_image_urls"] = tree.xpath("//picture//source/@srcset")
        
        # property_type
        ptype_list = tree.xpath("//span[@aria-label='Type']/text()")
        item["property_type"] = ptype_list[0].strip() if ptype_list else None
        
        return item


    def run(self, max_pages=1):
        #run the scraper 
        next_url = self.base_url
        page_count = 0
        
        while next_url and page_count < max_pages:
            page_count += 1
            print(f"Processing Page {page_count}...")
            tree = self.get_dom(next_url)
            if tree is None:
                break
            
            # Extract listing links
            links = set(tree.xpath("//a[contains(@href,'details')]/@href"))
            
            # Filter and parse listings
            for href in links:
                if re.search(r"/property/details-\d+\.html$", href):
                    full_link = urljoin("https://www.bayut.bh", href)
                    # Add a small delay to be polite
                    time.sleep(0.5)
                    
                    listing_tree = self.get_dom(full_link)
                    if listing_tree is not None:
                        data = self.parse_property(full_link, listing_tree)
                        self.data_list.append(data)
                        print(f"Scraped: {data.get('title', 'No Title')}")

            # Pagination
            next_page_list = tree.xpath("//a[@title='Next']/@href")
            if next_page_list:
                next_url = urljoin("https://www.bayut.bh", next_page_list[0])
            else:
                next_url = None

        self.save_files()

    def save_files(self):
        """Saves scraped data to JSON and CSV."""
        if not self.data_list:
            print("No data collected.")
            return

        # Save JSON
        with open("properties.json", "w", encoding="utf-8") as f:
            json.dump(self.data_list, f, indent=4, ensure_ascii=False)
        print("Saved properties.json")

        # Save CSV
        try:
            with open("properties.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writeheader()
                for row in self.data_list:
                    # Clean up lists for CSV compatibility
                    csv_row = row.copy()
                    if isinstance(csv_row.get("amenities"), list):
                        csv_row["amenities"] = ", ".join(csv_row["amenities"])
                    if isinstance(csv_row.get("breadcrumb"), list):
                        csv_row["breadcrumb"] = " > ".join(csv_row["breadcrumb"])
                    if isinstance(csv_row.get("property_image_urls"), list):
                        csv_row["property_image_urls"] = "|".join(csv_row["property_image_urls"])
                    writer.writerow(csv_row)
            print("Saved properties.csv")
        except Exception as e:
            print(f"Error saving CSV: {e}")

if __name__ == "__main__":
    scraper = BayutScraper()
    # Scrape 1 page by default for testing, user can adjust
    scraper.run(max_pages=1)
