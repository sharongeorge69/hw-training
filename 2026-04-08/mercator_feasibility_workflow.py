########### C R A W L E R ##############


import requests

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9,ml;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://mercatoronline.si/brskaj',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

params = {
    'limit': '100',
    'offset': '1',
    'filterData[offset]': '0',
    'filterData[categories]': '14535405',
    'from': '100',
    '_': '1775630831052',
}

response = requests.get(
    'https://mercatoronline.si/products/browseProducts/getProducts',
    params=params,
    headers=headers,
)

data =response.json()
p = data['products'][0]['data']
product_name = p.get('name')
grammage_quantity = p.get('unit_quantity')
selling_price = p.get('normal_price')
regular_price = p.get('current_price')
price_per_unit = p.get('price_per_unit')
brand = p.get('brand_name')
unique_id = p.get('codewz')
rating = p.get('rating')
review = p.get("ratings_num")
pdp_url = p.get('url')



############ P A R S E R ############
import requests
from parsel import Selector

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,ml;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://mercatoronline.si/brskaj',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

response = requests.get(
    'https://mercatoronline.si/izdelek/17931243/kisla-smetana-mercator-20-m-m-400-g',
    headers=headers,
)
sel = Selector(text=response.text)
nutrional_information= sel.xpath("//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[contains(., 'Hranilne vrednosti')]/@href, '#')]//table").getall()
ingredients = sel.xpath("//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[contains(., 'Sestavine')]/@href, '#')]//p").get()
contact_address = sel.xpath("//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[contains(., 'Kontaktni naslov')]/@href, '#')]//p").get()
features = sel.xpath("//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[normalize-space()='Lastnosti']/@href, '#')]//p").get()
instruction_for_use = sel.xpath("//div[contains(@class, 'tab-pane')][@id = substring-after(//ul[contains(@class, 'nav-tabs')]//a[normalize-space()='Navodila za uporabo']/@href, '#')]//p").get()


