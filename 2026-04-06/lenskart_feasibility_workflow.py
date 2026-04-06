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
