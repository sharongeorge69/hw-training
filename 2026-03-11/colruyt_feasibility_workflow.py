





headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}


######################  PARSER  ######################


from curl_cffi import requests
url = "https://www.colruyt.be/nl/producten/5331"
response = requests.get(url, headers=headers, impersonate="chrome110")
sel = Selector(text=response.text)
unique_id = sel.xpath(
    '//div[@data-vue="participatingProducts"]/@data-product-id'
).get()
product_name = sel.xpath("//h1[@class='title hide-sm']/text()").get()
competitor_name = "colruyt"
brand = sel.xpath("//div[@class='product-detail__title-container']//a/text()").extract_first()
grammage_quantity = sel.xpath('normalize-space(//h1[contains(@class,"title") and contains(@class,"hide-sm")]//span)').get()
grammage_unit = sel.xpath('normalize-space(//h1[contains(@class,"title") and contains(@class,"hide-sm")]//span)').get()
breadcrumbs = sel.xpath(
    '//li[@itemtype="https://schema.org/ListItem"]//span[@itemprop="name"]/text()'
).getall()
allergens = sel.xpath(
    'normalize-space(//div[contains(@class,"product-detail__allergen")]//li)'
).get()

product_unique_key = f"{unique_id}P"

#price is loaded from api
url = 'https://apip.colruyt.be/gateway/emec.colruyt.protected.bffsvc/cg/nl/api/5331/alternatives?placeId=604&limit=6'

resp = requests.get(
            url,
            impersonate="chrome120",
        )

selling_price = resp.json()['products'][0]['price']['basicPrice']
promotion_price= data['products'][0]['price']['quantityPrice']
promotion_valid_from = data['products'][0]['promotion'][0]['publicationStartDate']
promotion_valid_upto = data['products'][0]['promotion'][0]['publicationEndDate']
price_valid_from = data['products'][0]['promotion'][0]['publicationStartDate']
price_per_unit = data['products'][0]['promotion'][0]['measurementUnitPrice']
curreny = "euro"
product_description = data['products'][0]['description']
image_url_1 = data['products'][0]['squareImage']
alchol_by_volume = sel.xpath(
    '//ul[contains(@class,"product-detail__lifestyles")]//li/text()'
).getall()
site_shown_uom = sel.xpath('normalize-space(//h1[contains(@class,"title") and contains(@class,"hide-sm")]//span)').get()
instock = data['products'][0]['isPriceAvailable']
