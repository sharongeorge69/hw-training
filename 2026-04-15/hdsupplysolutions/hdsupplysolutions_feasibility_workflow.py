
############## C R A W L E R #####################
import requests
from parsel import Selector

url = "https://hdsupplysolutions.com/sitemap-product-1.xml"

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'accept': 'application/xml,text/xml;q=0.9,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
}

response = requests.get(url, headers=headers)

selector = Selector(text=response.text, type='xml')
raw_urls = selector.xpath('//*[local-name()="loc"]/text()').getall()
product_urls = [u for u in raw_urls if "/p/" in u]



########## P A R S E R ##################

import requests

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://hdsupplysolutions.com/p/chair-mats-00-125-120/homemat-multi-purpose-floor-protector-30-x-48-p324277',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
}


response = requests.get(
    'https://hdsupplysolutions.com/p/king-1500w-120v-small-gray-portable-utility-heater-space-p321981',
    headers=headers,
)
from parsel import Selector
import re
import json

sel = Selector(text=response.text)
product_category = sel.xpath('//input[@id="currentCategoryName"]/@value').get()
product_description =sel.xpath('//li[@data-hds-tag="product-details__detail-item"]/text()').getall()
script = sel.xpath('//script[contains(text(),"digitalData.product")]/text()').get()
match = re.search(r'digitalData\.product\s*=\s*(\[.*?\]);', script, re.S)

data = json.loads(match.group(1))
product = data[0]
vendor_seller_part_number = product.get("productId")
item_name = product.get("productName")
brand = product.get("brand")
mpn = product.get("mfgPart")
origin = product.get("origin")
