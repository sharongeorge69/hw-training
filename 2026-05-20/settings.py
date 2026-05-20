import os
from datetime import datetime

PROJECT_NAME = "blinkit"
BASE_URL = "https://blinkit.com"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'access_token': 'null',
    'app_client': 'consumer_web',
    'app_version': '1010101011',
    'auth_key': 'c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477',
    'content-type': 'application/json',
    'device_id': '4794eb9ea307bcd6',
    'is-response-compression-enabled': 'false',
    'lat': '28.4132534',
    'lon': '77.07271589999999',
    'origin': 'https://blinkit.com',
    'priority': 'u=1, i',
    'referer': 'https://blinkit.com/prn/super-crustless-white-bread/prid/503609',
    'rn_bundle_version': '1009003012',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'session_uuid': 'ae87b5da-3d9a-4f26-881f-0c31f31c04cd',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'web_app_version': '1008010016',
    'x-age-consent-granted': 'false',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
FILE_NAME_FULLDUMP = os.path.join(BASE_DIR, f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_sample.csv")
EXPORT_LIMIT = 100


SAMPLE_URLS = [
    {
        "pdp_url": "https://blinkit.com/prn/super-crustless-white-bread/prid/503609",
        "lat": "23.2539703",
        "lon": "69.67109669999999"
    }
]