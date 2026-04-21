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

BREADCRUMBS_XPATH = '//a[contains(@class, "breadcrumbs__link")]/text()'
UPC_XPATH = '//div[contains(@class, "mt-3") and contains(strong, "UPC")]/text()[normalize-space()]'
INVENTORY_SCRIPT_XPATH = '//script[@data-product-inventory-json]/text()'
JSON_LD_XPATH = '//script[@type="application/ld+json"]/text()'
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    response = page.goto(test_url, wait_until="load")
    html = page.content()
    selector = Selector(text=html)
    json_ld_data = selector.xpath(JSON_LD_XPATH).getall()
    item_name = json_ld_data.get('name', '')
    brand_name = json_ld_data.get('brand', {}).get('name', '')
    vendor_seller_part_number = json_ld_data.get('sku', '')
    offers = json_ld_data.get('offers', {})
    price_val = offers[0].get('price', '')
    description = json_ld_data.get('description', '')
    categories = selector.xpath(BREADCRUMBS_XPATH).getall()
    upc = selector.xpath(UPC_XPATH).get()
    inventory_script = selector.xpath(INVENTORY_SCRIPT_XPATH).get()
    raw_uoi = selector.xpath('//*[local-name()="tr"][.//td[normalize-space(.)="Case Pack"]]/td[last()]/text()').get()
    country_of_origin = selector.xpath('//*[local-name()="tr"][.//td[normalize-space(.)="Country of Origin"]]/td[last()]/text()').get()
