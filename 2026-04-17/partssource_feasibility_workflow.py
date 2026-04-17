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
