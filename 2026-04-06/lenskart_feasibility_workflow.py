########### C R A W L E R ###########

import requests
import json
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://www.lenskart.com',
    'priority': 'u=1, i',
    'referer': 'https://www.lenskart.com/',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'x-accept-language': 'en',
    'x-api-client': 'desktop',
    'x-b3-traceid': '991775557887181',
    'x-country-code': 'AE',
    'x-country-code-override': 'AE',
    'x-session-token': '6aab15cb-3b36-4320-aa0c-517fa060e383',
}

base_url = 'https://api-gateway.juno.lenskart.com/v2/products/category/10971'

response = requests.get(base_url, headers=headers, timeout=10)
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
url = "https://www.lenskart.com/en-ae/lenskart-air-la-e13033-c1-eyeglasses.html"
response = requests.get(url, headers=headers, timeout=15)
selector = Selector(text=response.text)
script_content = selector.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
json_data = json.loads(script_content)
page_props = json_data.get('props', {}).get('pageProps', {})
data = page_props.get('data', {})
product_details = data.get('productDetailData', {})

############# FINDINGS ###############
#1. The site has location based blocking so we need to use proxies
#2. The block checking fails completely in server
