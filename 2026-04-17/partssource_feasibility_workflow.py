######### C R A W L E R #########

import requests
from parsel import Selector
INDEX_SITEMAP = "https://sitemaps.partssource.com/apollo/sitemap.xml"
response = requests.get(INDEX_SITEMAP, timeout=30)
selector = Selector(text=response.text, type='xml')
sub_sitemaps = selector.xpath('//*[local-name()="loc"]/text()').getall()     
response = requests.get(sub_sitemaps[0], timeout=60)
selector = Selector(text=response.text, type='xml')
all_urls = selector.xpath('//*[local-name()="loc"]/text()').getall()
product_urls = [u for u in all_urls if u.startswith("https://www.partssource.com/parts/")]



#########  P A R S E R #########

import requests
import json
url = "https://www.partssource.com/parts/mesa-laboratories-inc/210427001"


marker = "window.__PRELOADED_STATE__ ="
start = html.find(marker)


headers = {"User-Agent": "Mozilla/5.0"}
html = requests.get(url, headers=headers).text


data = json.loads(json_text)

product = data.get("currentProduct", {}).get("product", {})
option = data.get("currentProduct", {}).get("selectedOption", {})
Manufacturer_Name = product.get("manufacturer")
Brand_Name = product.get("manufacturer")
Manufacturer_Part_Number = product.get("displayPartNumber")
Vendor_Seller_Part_Number = option.get("vendorItemNumber")
Item_Name = product.get("title")
Full_Product_Description = product.get("description")
Price = option.get("price") or product.get("price")
Unit_of_Issue = option.get("unitOfMeasurement")
Model_Number = product.get("models")
Product_Category = product.get("categories")
Availability = option.get("inventory") or product.get("availability")



