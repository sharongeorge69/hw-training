########### C R A W L E R ###########

import requests
import json
headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.lenskart.com',
        'referer': 'https://www.lenskart.com/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-api-client': 'desktop',
        'x-country-code': 'IN',
        'x-customer-type': 'NEW',
        'x-accept-language': 'en',
    }

base_url = 'https://api-gateway.juno.lenskart.com/v2/products/category/4062'

response = requests.get(url, headers=headers, timeout=10)
data = response.json()
result = data.get('result', {})
products = result.get('product_list', [])
pdp_url = products[0].get('product_url')


########### P A R S E R ###########
import requests
from parsel import Selector
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    }

response = requests.get(url, headers=headers, timeout=15)
selector = Selector(text=response.text)
script_content = selector.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
json_data = json.loads(script_content)
widgets = json_data.get('props', {}).get('pageProps', {}).get('data', {}).get('productDetailData', {}).get('result', [])
w_id = widgets.get('id')
w_data = widgets.get('data', {})
prices = w_data.get('prices', [])

#Sales price
sale_price = prices.get('price')

#Listed price
listed_price = prices.get('price')


options = w_data.get('options', [])
#frame colors
frame_colors = [item.get('title') for item in opt.get('optionList', [])]
#frame sizes
frame_sizes = [item.get('title') for item in opt.get('optionList', [])]
#images
gallery_items = w_data.get('galleryWidget', {}).get('data', [])
image_urls = [item.get('imageUrl') for item in gallery_items if item.get('type') == 'IMAGE']

product_details = w_data.get('specifications', [])


