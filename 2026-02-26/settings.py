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
from datetime import datetime
FILE_NAME_FULLDUMP = f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_{'sample'}.csv"
EXTRACTION_DATE = datetime.now().strftime('%Y-%m-%d')

# cookies = {
#     'nms_mgo_city': 'Mumbai',
#     'nms_mgo_state_code': 'MH',
#     '_fbp': 'fb.1.1772076946348.1099775985',
#     'WZRK_G': 'ade8e003947b48eeb57a73b364f3bc8c',
#     '_gcl_au': '1.1.1302236013.1772076947',
#     '_ALGOLIA': 'anonymous-a9f6add1-4fff-43f2-abc2-b8b35a80d3a4',
#     '_gid': 'GA1.2.831326066.1772076950',
#     '_ga': 'GA1.1.1524223469.1772076947',
#     'nms_mgo_pincode': '400011',
#     'AKA_A2': 'A',
#     '__tr_luptv': '1772084322250',
#     'RT': '"z=1&dm=www.jiomart.com&si=7c334fb7-2b75-471f-aa32-93ac002712d7&ss=mm2wux5k&sl=e&tt=7sz&obo=8&rl=1"',
#     '_ga_XHR9Q2M3VV': 'GS2.1.s1772084320$o3$g1$t1772084326$j54$l0$h1881054932',
#     'WZRK_S_88R-W4Z-495Z': '%7B%22p%22%3A2%2C%22s%22%3A1772084322%2C%22t%22%3A1772084327%7D',
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


json_data = {
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
    'pageToken': 'QjZ1gTY3gDO1ADNy0CZhJWOtcDN0ITLwADMw0SZlNmMyYWY2QiGC4K7iWOEG08jhWOCMIBM1IgC',
    'orderBy': 'attributes.popularity desc',
    'filter': 'attributes.status:ANY("active") AND attributes.category_ids:ANY("29009") AND (attributes.available_regions:ANY("U1RU", "PANINDIAGROCERIES")) AND (attributes.inv_stores_1p:ANY("ALL", "U456") OR attributes.inv_stores_3p:ANY("ALL", "groceries_zone_non-essential_services", "general_zone", "groceries_zone_essential_services"))',
    'visitorId': 'anonymous-403fb6f0-c24b-4de9-8633-51b2f584c7c8',
}
