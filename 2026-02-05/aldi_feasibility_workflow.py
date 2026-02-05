import requests
from parsel import Selector
from datetime import datetime
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}


#category_url extraction
url = "https://www.aldi.us/sitemap.html"
response = requests.get(url, headers=headers)

selector = Selector(text=response.text)

product_links = selector.xpath('//a[contains(@class, "base-navigation-tree__link") and starts-with(@href, "/products/")]/@href').getall()


######################crawler######################

url = "https://www.aldi.us/products/snacks/chips-crackers-popcorn/k/127"
response = requests.get(url, headers=headers)
selector = Selector(text=response.text)

#extract product urls
product_urls = selector.xpath("//div[contains(@class, 'product-tile')]//a[contains(@class, 'product-tile__link')]/@href").getall()
for product in product_urls:
    full_product_url = f"https://www.aldi.us{product}"  
#pagination
next_page = selector.xpath('//a[@aria-label="Next"]/@href').get()

######################Parser######################

url = "https://www.aldi.us/product/elevation-nacho-cheese-protein-puffs-2-1-oz-0000000000012048"

response = requests.get(url, headers=headers)
selector = Selector(text=response.text)
competitor_name = "aldi"
extraction_date = datetime.now().strftime("%Y-%m-%d")
product_name = selector.xpath("//h1[contains(@class, 'product-details__title')]/text()").get()
brand = selector.xpath('//a[contains(@class, "product-details__brand-name")]/text()').get()
breadcrumbs = selector.xpath("//nav[@aria-label='Breadcrumb']//a[contains(@class, 'breadcrumbs__item')]/text()").getall()
breadcrumb = " > ".join(breadcrumbs) if breadcrumbs else None
producthierarchy_level1 = breadcrumbs[0] if len(breadcrumbs) > 0 else None
producthierarchy_level2 = breadcrumbs[1] if len(breadcrumbs) > 1 else None
producthierarchy_level3 = breadcrumbs[2] if len(breadcrumbs) > 2 else None
currency = "USD"
pdp_url = url
description = '//div[contains(@class, "show-more__content")]//div[contains(@class, "base-rich-text")]'
country_of_origin = selector.xpath('//div[@id="origin"]//div[contains(@class, "base-accordion-item__content-inner")]/text()').get()
image_url_1 = selector.xpath('//img[contains(@class, "product-image__image")]/@src').get()
site_shown_uom = selector.xpath('//span[contains(@class, "product-details__unit-of-measurement")]/text()').get()
unique_id = url.split('-')[-1] if '-' in url else None
product_unique_key = f"{unique_id}P"
regular_price = selector.xpath('//span[contains(@class, "wasPrice_label")]/text()').get()
selling_price = selector.xpath('//span[contains(@class, "base-price__regular")]/span/text()').get()

percentage_discount = selector.xpath('//div[contains(@class, "discountLabel")]/text()').get()

#############################Findings############################

#126 fields where given but all fields are not available in the website