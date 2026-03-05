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

cookies_crawler = {
    'nms_mgo_city': 'Mumbai',
    'nms_mgo_state_code': 'MH',
    '_fbp': 'fb.1.1772161296788.92828821',
    'WZRK_G': '01b0a65e76e848b79c0977ecd7b3f458',
    '_gcl_au': '1.1.1687434808.1772161298',
    '_ga': 'GA1.1.1329720305.1772161298',
    'nms_mgo_pincode': '400001',
    'AKA_A2': 'A',
    '__tr_luptv': '1772183158773',
    '_ga_XHR9Q2M3VV': 'GS2.1.s1772182615$o5$g1$t1772183168$j49$l0$h998094909',
    'WZRK_S_88R-W4Z-495Z': '%7B%22p%22%3A14%2C%22s%22%3A1772182617%2C%22t%22%3A1772183168%7D',
    'RT': '"z=1&dm=www.jiomart.com&si=46980c59-ace0-4043-9b58-8dfe7e6e591e&ss=mm4nrtt3&sl=3&tt=1n5&obo=2&rl=1"',
}

headers_crawler = {
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

headers = headers_crawler.copy()

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
cookies_instock = {
    'AKA_A2': 'A',
    '_ALGOLIA': 'anonymous-e55bd270-15e8-4b6b-9eae-cd80c8a9791a',
    '_gid': 'GA1.2.2080288398.1772617558',
    '_fbp': 'fb.1.1772617558439.746346508',
    'WZRK_G': 'a6b76ee20e914a179ff3ead7a7650490',
    '_gcl_au': '1.1.573810863.1772617560',
    '_ga': 'GA1.1.1418950530.1772617558',
    'nms_mgo_pincode': '400001',
    'nms_mgo_city': 'Mumbai',
    'nms_mgo_state_code': 'MH',
    '__tr_luptv': '1772617993200',
    '_ga_XHR9Q2M3VV': 'GS2.1.s1772617559$o1$g1$t1772618045$j60$l0$h1208855012',
    'RT': '"z=1&dm=www.jiomart.com&si=7cb555f9-078f-4d75-aa8a-584106bf061f&ss=mmbuq5e6&sl=7&tt=4ud&obo=2&rl=1"',
    'WZRK_S_88R-W4Z-495Z': '%7B%22p%22%3A8%2C%22s%22%3A1772617558%2C%22t%22%3A1772618000%7D',
}

headers_instock = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.jiomart.com',
    'priority': 'u=0, i',
    'referer': 'https://www.jiomart.com',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

json_data_instock = {
    'identifier': 'c9af40f2-2003-49c6-aab3-de6e6d5cb0cf',
    'to_pincode': '400001',
    'customer_details': {
        'phone_number': '0',
        'pincode': '400001',
        'coordinates': {
            'lat': 18.933906932,
            'long': 72.838416529,
        },
    },
    'articles': [
        {
            'article_id': 'RVIKS25PAN',
            'vertical': 'GROCERIES',
            'lookup_inventory': True,
            'tenant_ids': [
                '1006',
            ],
            'merchant_id': None,
            'channel_id': None,
            'available_at_3p_seller': True,
            'available_at_1p_kirana': False,
            'available_at_rrl_fc': False,
            'available_at_rrl_store': False,
            'available_at_3p_kirana': False,
            'fulfillment_channel': '',
            'delivery_type': 'grab_and_go',
            'locked_phone': False,
            'transport_mode': None,
            'package_dimension': {
                'height': 13.5,
                'height_uom': 'cm',
                'length': 21,
                'length_uom': 'cm',
                'width': 17,
                'width_uom': 'cm',
                'weight': 1000,
                'weight_uom': 'gm',
                'volumetric_weight': 960,
                'volumetric_weight_uom': 'gm',
                'depth': 0,
                'depth_uom': 'cm',
            },
            'is_liquid': False,
            'is_hazmat': False,
            'is_fragile': False,
            'is_hvi': False,
            'ship_separate': False,
            'exchange_details': None,
            'qc': 1,
            'suspect': 1,
            'distance': 0.6083433185263083,
            'site_fallback': 0,
            'force_fit_store': 'T6HZ',
            'region': 'TXCF',
            'polygon_id': 'T6HZ_QC_5475bdd9',
        },
    ],
}
