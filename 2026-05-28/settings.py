import os
from datetime import datetime

PROJECT_NAME = "jiomart"

# MongoDB config
MONGO_URI = "mongodb://127.0.0.1:27017/"
MONGO_DB = f"{PROJECT_NAME}db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

# # Export
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
# FILE_NAME_FULLDUMP = os.path.join(BASE_DIR, f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_sample.csv")
# EXPORT_LIMIT = 200

# Crawler settings
BASE_URL = "https://www.jiomart.com"
API_URL = "https://www.jiomart.com/ext/vertex/application/api/v1.0/products"
PRODUCT_BASE_URL = "https://www.jiomart.com/product/"
MAX_RETRIES = 3

# headers = {
#     "sec-ch-ua-platform": '"Linux"',
#     "Authorization": "Bearer Njg1OTQ1ZjQ2YzhjN2FlZTNmM2FmNjA1OlRwS3c3d0Q5aA==",
#     "x-location-detail": '{"country":"INDIA","country_iso_code":"IN","city":"MUMBAI","pincode":"400054","state":"MAHARASHTRA"}',
#     "Referer": "",
#     "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
#     "sec-ch-ua-mobile": "?0",
#     "x-fp-signature": "v1.1:3433e0bef959206e692403da4c6c38fd32f72a2ff39bf8a4758686052f2f4ea8",
#     "x-fp-date": "20260528T065546Z",
#     "x-geolocation": '{"latitude":"19.0820116","longitude":"72.83446909999999","polygon_ids":["8687_QC_b7d05fe5","T7GZ_QC_5f0ed1d7"]}',
#     "x-fp-sdk-version": "1.10.3-60",
#     "Accept": "application/json, text/plain, */*",
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
#     "x-currency-code": "INR",
# }
headers = {
    'sec-ch-ua-platform': '"Linux"',
    'Authorization': 'Bearer Njg1OTQ1ZjQ2YzhjN2FlZTNmM2FmNjA1OlRwS3c3d0Q5aA==',
    'x-location-detail': '{"country":"INDIA","country_iso_code":"IN","city":"BENGALURU","pincode":"560003","state":"KARNATAKA"}',
    'Referer': '',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'x-fp-signature': 'v1.1:52cde52dd7ebb7b60e43450d6e862aa7c32a712264c07b550455cc96a683db23',
    'x-fp-date': '20260528T102512Z',
    'x-geolocation': '{"latitude":"13.0019142","longitude":"77.57133639999999","polygon_ids":["FR48_QC_b3b238e4","TB1G_QC_6c4cf65d"]}',
    'x-fp-sdk-version': '1.10.3-60',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'x-currency-code': 'INR',
}


# category_configs = [
#     {
#         "url": "https://www.jiomart.com/products?department=groceries&l3_category=detergent-powder-liquid",
#         "f": "l3_category:detergent-powder-liquid:::department:groceries:::journey:quickcommerce:::store_ids:3148||3462",
#         "name": "Detergent Powder & Liquid",
#     },
#     {
#         "url": "https://www.jiomart.com/products?department=groceries&l1_category=fresh-l1&l2_category=milk-milk-products&l3_category=milk",
#         "f": "l3_category:milk:::l2_category:milk-milk-products:::l1_category:fresh-l1:::department:groceries:::journey:quickcommerce:::store_ids:3148||3462",
#         "name": "Milk",
#     },
#     {
#         "url": "https://www.jiomart.com/products?department=groceries&l1_category=fresh-l1&l2_category=milk-milk-products&l3_category=butter-margarine",
#         "f": "l3_category:butter-margarine:::l2_category:milk-milk-products:::l1_category:fresh-l1:::department:groceries:::journey:quickcommerce:::store_ids:3148||3462",
#         "name": "Butter & Margarine",
#     },
#     {
#         "url": "https://www.jiomart.com/products?department=groceries&l1_category=home&l2_category=dishwash",
#         "f": "l2_category:dishwash:::l1_category:home:::department:groceries:::journey:quickcommerce:::store_ids:3148||3462",
#         "name": "Dishwash",
#     },
# ]


category_configs = [
    {
        "url": "https://www.jiomart.com/products?department=groceries&l3_category=detergent-powder-liquid",
        "f": "l3_category:detergent-powder-liquid:::department:groceries:::journey:quickcommerce:::store_ids:2371||215842||14829",
        "name": "Detergent Powder & Liquid",
    }

]
