
import requests
from lxml import etree
import settings


# Task 4: Custom Exception
class DataMiningError(Exception):
    pass


# Task 1: Class-Based Design
class BayutParser:
    def __init__(self):
        #basic requirements initialization
        self.url = settings.BASE_URL
        self.headers = settings.HEADERS
        self.raw_data = None

    def fetch_html(self):
        
        #Task 4: Fetch HTML with exception handling
        #Task 2: Store raw HTML
        
        try:
            print(f"Fetching URL: {self.url}")
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()

            self.raw_data = response.text
            self.save_to_file(self.raw_data, settings.RAW_FILE)

            print(f"Raw HTML saved to {settings.RAW_FILE}")

        except requests.exceptions.RequestException as error:
            raise DataMiningError(f"Network or response error: {error}")

    def parse_data(self):
        
        #Task 1: Parse fetched data
        #Task 4: Raise custom exception on parsing failure
        
        if not self.raw_data:
            raise DataMiningError("No HTML data available for parsing.")

        tree = etree.HTML(self.raw_data)
        listings = tree.xpath("//article")

        parsed_items = []

        for item in listings:
            try:
                title = item.xpath(".//h2/text()")
                price = item.xpath(".//span[@aria-label='Price']/text()")

                parsed_items.append({
                    "name": title[0].strip() if title else "N/A",
                    "price": price[0].strip() if price else None
                })

            except Exception as error:
                raise DataMiningError(f"Parsing failed: {error}")

        return parsed_items

    def parse_item(self):
        return self.parse_data()

    def filter_and_save(self, data):
        
        #Task 6: List comprehension for filtering
        cleaned_names = [
            item["name"]
            for item in data
            if item["price"] is not None
        ]
        #storing cleaned data to cleaned_data.txt
        with open(settings.CLEAN_FILE, "w", encoding="utf-8") as file:
            for name in cleaned_names:
                file.write(f"{name}\n")

        print(f"Cleaned data saved to {settings.CLEAN_FILE}")

    def save_to_file(self, content, filename):
        
        #Task 2: File operations - writing raw html contents to raw.html
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

    def yield_lines_from_file(self, filename):
        
        #Task 3: Generator for memory-efficient reading
        
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                yield line.strip()

    def start(self):
        #Task 1: Start crawling and processing
        
        self.fetch_html()
        parsed_data = self.parse_item()
        self.filter_and_save(parsed_data)

    def close(self):
        #Task 1: Close connections
        print("Data mining process completed.")


if __name__ == "__main__":
    parser = BayutParser()

    try:
        parser.start()
        for name in parser.yield_lines_from_file(settings.CLEAN_FILE):
            print(f"Property Name: {name}")

    except DataMiningError as error:
        print(f"ERROR: {error}")

    finally:
        parser.close()
