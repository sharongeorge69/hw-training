PROJECT_NAME = "grainger"
BASE_URL = "https://www.grainger.com"
SITEMAP_INDEX_URL = "https://www.grainger.com/sitemap_index.xml"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.grainger.com/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'upgrade-insecure-requests': '1',
}

cookies = {
    'BRC': 'B',
    'sitetype': 'full',
    'AB1': 'G',
    'AD1': 'B',
    'TLTSID': '7F2E327A8CB3B788F8856BAF128F0502',
    'signin': 'C',
    'reg': 'A',
    'LDC': '7F2E327A8CB3B788F8856BAF128F0502',
    'JSESSIONID': '19573F329A65B1AF11020AC4FB255FF1.7383125b',
    'datadome': '1VQiY9SV~vwfP_Ck5iwoVuWsTunioSRUTNhGcQriSvEThMOD7IaOXBtERr5L_k1cpmiHIvICqJn4Ly~9iWVfK2Vwkaz37aq_TD_iPDudqXFPd_jwEss_8n97uGdwGY7n',
}

import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
