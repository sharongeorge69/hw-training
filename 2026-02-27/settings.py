# basic details
PROJECT = ""
PROJECT_NAME = "jiomart"
BASE_URL = "https://www.jiomart.com/"
CRAWLER_URL = "https://www.jiomart.com/trex/search"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

# MONGO_URI = "mongodb://localhost:27017/"
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

# Export settings
import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME_FULLDUMP = os.path.join(BASE_DIR, f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_{'sample'}.csv")
EXTRACTION_DATE = datetime.now().strftime('%Y-%m-%d')

# cookies = {
#     'nms_mgo_city': 'Mumbai',
#     'nms_mgo_state_code': 'MH',
#     '_fbp': 'fb.1.1772161296788.92828821',
#     'WZRK_G': '01b0a65e76e848b79c0977ecd7b3f458',
#     '_gcl_au': '1.1.1687434808.1772161298',
#     '_ga': 'GA1.1.1329720305.1772161298',
#     'nms_mgo_pincode': '400001',
#     'AKA_A2': 'A',
#     '__tr_luptv': '1772183158773',
#     '_ga_XHR9Q2M3VV': 'GS2.1.s1772182615$o5$g1$t1772183168$j49$l0$h998094909',
#     'WZRK_S_88R-W4Z-495Z': '%7B%22p%22%3A14%2C%22s%22%3A1772182617%2C%22t%22%3A1772183168%7D',
#     'RT': '"z=1&dm=www.jiomart.com&si=46980c59-ace0-4043-9b58-8dfe7e6e591e&ss=mm4nrtt3&sl=3&tt=1n5&obo=2&rl=1"',
# }

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.jiomart.com',
    'priority': 'u=1, i',
    'referer': 'https://www.jiomart.com/c/groceries/biscuits-drinks-packaged-foods/tea-coffee/29009',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}

headers_price_api = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'pin': '400001',
    'priority': 'u=1, i',
    'referer': 'https://www.jiomart.com/p/groceries/hasmukhrai-co-hotel-mixture-no-02-500g/609581169',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

json_data_price = {
    'pageCategories': [
        'PDP Variants',
    ],
    'pageSize': 1,
    'visitorId': 'anonymous-28edee8a-e09b-4d62-8105-77ee466dc366',
    'filter': 'attributes.status:ANY("active")',
    'searchMode': 'PRODUCT_SEARCH_ONLY',
    'branch': 'projects/sr-project-jiomart-jfront-prod/locations/global/catalogs/default_catalog/branches/0',
}

json_data_crawler = {
    'pageSize': 50,
    'facetSpecs': [
        {
            'facetKey': {
                'key': 'brands',
            },
            'limit': 500,
            'excludedFilterKeys': [
                'brands',
            ],
        },
        {
            'facetKey': {
                'key': 'categories',
            },
            'limit': 500,
            'excludedFilterKeys': [
                'categories',
            ],
        },
        {
            'facetKey': {
                'key': 'attributes.category_level_4',
            },
            'limit': 500,
            'excludedFilterKeys': [
                'attributes.category_level_4',
            ],
        },
        {
            'facetKey': {
                'key': 'attributes.category_level_1',
            },
            'excludedFilterKeys': [
                'attributes.category_level_4',
            ],
        },
        {
            'facetKey': {
                'key': 'attributes.avg_selling_price',
                'return_min_max': True,
                'intervals': [
                    {
                        'minimum': 0.1,
                        'maximum': 100000000,
                    },
                ],
            },
        },
        {
            'facetKey': {
                'key': 'attributes.avg_discount_pct',
                'return_min_max': True,
                'intervals': [
                    {
                        'minimum': 0,
                        'maximum': 99,
                    },
                ],
            },
        },
    ],
    'variantRollupKeys': [
        'variantId',
    ],
    'branch': 'projects/sr-project-jiomart-jfront-prod/locations/global/catalogs/default_catalog/branches/0',
    'pageCategories': [
        '29009',
    ],
    'userInfo': {
        'userId': None,
    },
    'pageToken': 'U2MlNWZzQmN4IzYz0iZihDOtczY2ITLwADMw0SNkZ2MkRzY2QiGB8v3lrJEG0sqoPMCMIBM1IgC',
    'orderBy': 'attributes.popularity desc',
    'filter': 'attributes.status:ANY("active") AND attributes.category_ids:ANY("29009") AND (attributes.available_regions:ANY("TXCF", "PANINDIAGROCERIES")) AND (attributes.inv_stores_1p:ANY("ALL", "T7GZ") OR attributes.inv_stores_3p:ANY("ALL", "groceries_zone_non-essential_services", "general_zone", "groceries_zone_essential_services"))',
    'visitorId': 'anonymous-9e203381-835d-40cd-8b12-4737626d226b',
}
