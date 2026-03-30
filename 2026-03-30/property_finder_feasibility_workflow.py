





############## P A R S E R ####################
# Parser logic for sales properties
import requests

headers = {
    'x-nextjs-data': '1',
    'sec-ch-ua-platform': '"Linux"',
    'Referer': 'https://www.propertyfinder.ae/en/transactions/rent/dubai?period=3y&fu=0&rp=y&ob=mr',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
}

params = {
    'category': 'buy',
    'slug': 'dubai',
    'period': '3y',
    'fu': '0',
    'ob': 'mr',
}

response = requests.get(
    'https://www.propertyfinder.ae/dataguru/_next/data/XGjX_O5nJ3BtMoyVkdeZg/en/transactions/buy/dubai.json',
    params=params,
    headers=headers,
)

data = response.json()

transactions = data['pageProps']['list']['transactionList']

# Parser logic for rental properties
import requests

headers = {
    'x-nextjs-data': '1',
    'sec-ch-ua-platform': '"Linux"',
    'Referer': 'https://www.propertyfinder.ae/en/transactions/buy/dubai/dubai-land-liwan-wavez-residence?fu=0&ob=mr',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
}

params = {
    'category': 'rent',
    'slug': [
        'dubai',
        'dubai-land-liwan-wavez-residence',
    ],
    'fu': '0',
    'rp': 'y',
    'ob': 'mr',
}

response = requests.get(
    'https://www.propertyfinder.ae/dataguru/_next/data/XGjX_O5nJ3BtMoyVkdeZg/en/transactions/rent/dubai/dubai-land-liwan-wavez-residence.json',
    params=params,
    headers=headers,
)

data = response.json()

transactions = data['pageProps']['list']['transactionList']


################# FINDINGS ####################

#filter applying logic

#1. make request to the Location Discovery API (https://www.propertyfinder.ae/api/pwa/location/list?l_t=TOWER%2CSUBCOMMUNITY%2CCOMMUNITY&c=1&locale=en) to extract the slugs required to slice the transactions by location
#2. make request to the transaction API  endpoint = f"https://www.propertyfinder.ae/dataguru/_next/data/{build_id}/en/transactions/{category}/dubai/{SLUG}.json"
#3. if the totalTransactionCount is greater than 500 make request to the transaction API with different filter parameters (Property Type, Bedrooms, Price Range, etc) to get the transactions in batches



