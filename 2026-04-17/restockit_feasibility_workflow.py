############## C R A W L E R ##############

from camoufox.sync_api import Camoufox
from parsel import Selector

MAIN_SITEMAP = "https://www.restockit.com/sitemap.xml"
with Camoufox(headless=True) as browser:
        page = browser.new_page()
response = page.goto(MAIN_SITEMAP, wait_until="load", timeout=60000)
content = response.body().decode('utf-8')
selector = Selector(text=content, type='xml')
product_sitemaps = selector.xpath('//*[local-name()="loc"][contains(text(), "sitemap_products")]/text()').getall()
response = page.goto(product_sitemaps[0], wait_until="load", timeout=60000)
content = response.body().decode('utf-8')
selector = Selector(text=content, type='xml')
urls = selector.xpath('//*[local-name()="loc"]/text()').getall()
product_urls = [url for url in urls if "/products/" in url]


############# P A R S E R ###############

from camoufox.sync_api import Camoufox
from parsel import Selector

test_url = "https://www.restockit.com/products/3m-peltor-x-series-earmuffs-num-mmmx5a"
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    response = page.goto(test_url, wait_until="load")
    html = page.content()
    selector = Selector(text=html)
    json_ld_scripts = selector.xpath('//script[@type="application/ld+json"]/text()').getall()
    item_name = selector.css('h1.product__title::text').get() 

    brand_name = selector.css('.product-vendor a::text').get() 
    upc = selector.xpath('//div[contains(@class, "mt-3") and contains(strong, "UPC")]/text()[normalize-space()]').get()
    inventory_script = selector.css('script[data-product-inventory-json]::text').get()
    categories = selector.css('.breadcrumbs__link::text').getall()
    description = selector.css('.accordion__content::text').get() 
    price_text = selector.css('.price__current::text').get()
    sku_text = selector.css('.product__sku::text').get()
