###################FEASIBILITY_WORKFLOW######################


#####################Crawler######################


import requests

category_id = "29009"

url = "https://www.jiomart.com/trex/search"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://www.jiomart.com",
    "Referer": f"https://www.jiomart.com/c/groceries/-/-/{category_id}"
}
session = requests.Session()
session.headers.update(headers)
payload = {
        "pageSize": 50,
        "pageCategories": [str(category_id)],
        "filter": f'attributes.status:ANY("active") AND attributes.category_ids:ANY("{category_id}")',
        "visitorId": visitor_id
    }
response = session.post(url, json=payload)
data = response.json()
results = data.get("results", [])
for r in results:
    product_data = r.get("product", {})
    variants = product_data.get("variants", [])
    pdp_url = variants[0].get("uri")
    pdp_url = "https://www.jiomart.com" + pdp_url

######################Parser######################
from curl_cffi import requests

headers = {
    'Referer': 'https://www.jiomart.com/?tab=groceries',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
 }
     
response = requests.get(
    'https://www.jiomart.com/c/groceries/biscuits-drinks-packaged-foods/tea-coffee/29009',
    headers=headers,impersonate="chrome110"
)
from parsel import Selector
sel = Selector(response.text)

#fields
competitor_name = "jiomart"
product_name = sel.xpath('//div[@id="pdp_product_name"]//text()').get()
brand = sel.xpath('//div[@class="product-header-brand-text"]//a[@id="top_brand_name"]/text()').get()
breadcrumbs = sel.xpath('//ul[@class="jm-breadcrumbs-list"]//a/text()').getall()
producthierarchy_level1 = sel.xpath("(//ul[@class='jm-breadcrumbs-list']/li)[1]/a/text()").get()
producthierarchy_level2 = sel.xpath("(//ul[@class='jm-breadcrumbs-list']/li)[2]/a/text()").get()
producthierarchy_level3 = sel.xpath("(//ul[@class='jm-breadcrumbs-list']/li)[3]/a/text()").get()
package_sizeof_sellingprice = sel.xpath('//tr[th[contains(text(), "Pack Of")]]/td/text()').get()
currency = "INR"
product_description = sel.xpath("//div[@id='pdp_description']//text()[normalize-space()]").get()
storage_instructions = sel.xpath('//tr[th[contains(text(), "Storage Category")]]/td/text()').get()
instructionforuse = sel.xpath('//tr[th[contains(text(), "How To Use")]]/td/text()').get()
country_of_origin = sel.xpath('//tr[th[contains(text(), "Country of Origin")]]/td/text()').get()
manufacturer_address = sel.xpath('//tr[th[contains(text(), "Manufacturer Address")]]/td/text()').get()
product_unique_key = f"{unique_id}P"
img_urls = sel.xpath(
"//div[contains(@class,'product-image-carousel-thumb')]"
"//div[contains(@class,'swiper-thumb-slides')]//img/@data-src | "
"//div[contains(@class,'product-image-carousel-thumb')]"
"//div[contains(@class,'swiper-thumb-slides')]//img/@src"
).extract()

height = sel.xpath('//tr[th[contains(text(), "Height")]]/td/text()').extract_first()
length = sel.xpath('//tr[th[contains(text(), "Length")]]/td/text()').extract_first()
width = sel.xpath('//tr[th[contains(text(), "Width")]]/td/text()').extract_first()

dimensions = ""
if length and width and height:
    dimensions = f"{length}X{width}X{height}"

#additional request for selling_price, regular_price, discount

url = "https://www.jiomart.com/trex/search"
payload = json_data.copy()
payload['filter'] = f'attributes.product_id:ANY("{unique_id}")'
payload['pageSize'] = 1
response = requests.post(url, cookies=cookies, headers=headers, json=payload, timeout=15, impersonate="chrome110")

data = response.json()
results = data.get("results", [])
product = results[0].get("product", {})
variants = product.get("variants", [])
variant = variants[0]
attributes = variant.get("attributes", {})
buybox_mrp = attributes.get("buybox_mrp", {}).get("text", [])
gtm_details = variant.get("gtm_details", {})
txcf_data = next((entry for entry in buybox_mrp if entry.startswith("TXCF|")), None)
regular_price = parts[4]
selling_price = parts[5]
percentage_discount = parts[8] if len(parts) > 8 else ""

#additional request for rating and review

rating_headers = {
            'vertical': 'jiomart',
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
rating_url = f"https://reviews-ratings.jio.com/customer/op/v1/review/product-statistics/{alternate_id/unique_id}"
rating_resp = requests.get(rating_url, headers=rating_headers, timeout=10)
details = rating_resp.json()
data = details.get("data", {})
rating = data.get("averageRating", "")
review = data.get("ratingsCount", "")

#############findings##############

#1. pricing information returned by the product API does not consistently align with the pricing displayed on the website frontend.
