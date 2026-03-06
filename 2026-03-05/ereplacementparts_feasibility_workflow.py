
######################C A T E G O R Y_C R A W L E R########################

import requests
from parsel import Selector

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}

# 1. Get all main category links (from Sitemap)
response = requests.get('https://www.ereplacementparts.com/sitemap/', headers=headers)
sel = Selector(text=response.text)
main_categories = sel.xpath("//a[contains(@class, 'text-lg underline')]/@href").getall()


# 2. Inside a main category (e.g. Appliance), get all subcategory/brand links
response = requests.get('https://www.ereplacementparts.com/parts/appliance/', headers=headers)
sel = Selector(text=response.text)
subcategory_links = sel.xpath("//*[@id='ShopByBrand']/following-sibling::ul[1]//a/@href").getall() 

# 3. Drill down to a specific Brand/Category intersection (Terminal Discovery)
# (e.g. Dishwasher -> Bosch Models)
response = requests.get('https://www.ereplacementparts.com/parts/appliance/dishwasher/bosch/models/', headers=headers)
sel = Selector(text=response.text)

# Extract total count and specific terminal page links (individual models)
total_count = sel.xpath("//div[@class='summary']/text()").get() 
terminal_links = sel.xpath("//ul[contains(@class, 'mini-model-icons')]//a/@href").getall()


####################### C R A W L E R ############################

# Extract PDP links from a Terminal Page
response = requests.get(
    'https://www.ereplacementparts.com/parts/appliance/dishwasher/bosch/bearings/',headers=headers,
)
sel = Selector(text=response.text)
links = sel.xpath("//div[contains(@class,'nf__part-lg')]//a[contains(@class,'nf__part-lg__title')]/@href").getall()
for link in links:
    full_link = f"https://www.ereplacementparts.com/{link}"


#####################P A R S E R########################
import requests
from parsel import Selector

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.ereplacementparts.com/parts/appliance/refrigerator/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

response = requests.get(
    'https://www.ereplacementparts.com/parts/refrigerator/frigidaire/erp734936/door-shelf-retainer-bar-240534701/',
    headers=headers,
)

sel = Selector(text=response.text)

title = sel.xpath('//h1[@itemprop="name"]//text()').get()

manufacturer = sel.xpath('//dd[@itemprop="brand"]//span[@itemprop="name"]//text()').extract_first()

price = sel.xpath('//span[@itemprop="price"]//text()').extract_first()

description = sel.xpath('//p[@itemprop="description"]//text()').extract_first()

availability = sel.xpath('//span[@itemprop="availability"]//text()').get()

imageurls = sel.xpath(
    "//div[@class='pd__img']//@src | "
    "//div[@class='pd__img']//@data-large-src | "
    "//div[@class='pd__img']//@data-med-src"
).getall()

input_part_number = sel.xpath('//dd[@itemprop="mpn"]//text()').extract_first()


equivalent_part_number = sel.xpath("//div[contains(text(),'replaces these')]/following-sibling::ul[1]/li/text()").getall()

compatible_products = sel.xpath(
    "//div[contains(@class,'pd__crossref')]//tbody//tr/td[2]/a/text()"
).getall()
