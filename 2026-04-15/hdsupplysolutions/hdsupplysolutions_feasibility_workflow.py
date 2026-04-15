
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

