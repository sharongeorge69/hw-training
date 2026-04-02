


############# C R A W L E R ##########
import requests
from parsel import Selector
headers = {
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }
target_url = "https://www.moglix.com/brands/l-t/electricals/circuit-breakers-fuses/mcb/211124500"
params = {
    'page': '1',
}
response = requests.get(target_url, headers=headers, params=params,)
selector = Selector(text=response.text)
links = selector.xpath('//a[contains(@href, "/mp/")]/@href').getall()



########## P A R S E R ###########

import requests
from parsel import Selector
import json
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

response = requests.get(url, headers=headers)
selector = Selector(text=response.text)
script_text = selector.xpath("//script[@id='ssr-pwa-state']/text()").get()
json_str = script_text.replace('&q;', '"')
data = json.loads(json_str)
product_key = next((k for k in data.keys() if str(k).startswith("product-")), None)
product_data = data[product_key].get("data", {})
product_group = product_data.get("productGroup", {})

product_name = product_group.get("productName")
product_specifications = product_group.get("productAttributes", {})
product_description = product_group.get("productDescripton")
product_features = product_group.get("productKeyFeatures")
product_images_url = []
product_video_url = product_group.get("productVideos", [])

