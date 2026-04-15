############## C R A W L E R #####################

import requests
from parsel import Selector

url = "https://www.officedepot.com/product_sitemap_0.xml"

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'accept': 'application/xml,text/xml;q=0.9,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
}

response = requests.get(url, headers=headers, timeout=30)
selector = Selector(text=response.text, type='xml')
urls = selector.xpath('//*[local-name()="loc"]/text()').getall()


################ P A R S E R ##################

import requests
import re
import json
from parsel import Selector

# Target URL
target_url = "https://www.officedepot.com/a/products/431632/HP-952XL952-High-Yield-Black-And/#Specs"
base_url = target_url.split('#')[0]

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
}

print(f"Fetching Product Page: {base_url}")
response = requests.get(base_url, headers=headers, timeout=30)
sel = Selector(text=response.text)
script = sel.xpath(
    '//script[contains(text(),"SKUPAGE_INITIAL_STATE")]/text()'
).get()
match = re.search(r'window\.SKUPAGE_INITIAL_STATE\s*=\s*({.*});', script, re.S)

raw_json = match.group(1)
clean_json = raw_json.replace("undefined", "null")
data = json.loads(clean_json)

catalog = data["fetchData"]["skuInfo"]["catalog"]
sku = data["fetchData"]["skuInfo"]["skuDetails"]


item_name = catalog.get("title")
brand = catalog.get("brand")
price = sku.get("price", {}).get("sellPrice", {}).get("price")
sku_id = sku.get("skuId")
upc = catalog.get("upc")

