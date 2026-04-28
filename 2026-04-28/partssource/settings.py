PROJECT_NAME = "partssource"
BASE_URL = "https://www.partssource.com"
SITEMAP_URL = "https://sitemaps.partssource.com/apollo/sitemap.xml"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

# Raw response DB
MONGO_RAW_RESPONSE_DB = f"{PROJECT_NAME}_raw_response_db"
MONGO_COLLECTION_RAW_RESPONSE = f"{PROJECT_NAME}_raw_response"

# MONGO_URI = "mongodb://127.0.0.1:27017/"
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
}

PROXIES_LIST = [
    "http://snnsexta:qoakdgquffb0@31.59.20.176:6754/",
    "http://snnsexta:qoakdgquffb0@198.23.239.134:6540/",
    "http://snnsexta:qoakdgquffb0@45.38.107.97:6014/",
    "http://snnsexta:qoakdgquffb0@107.172.163.27:6543/",
    "http://snnsexta:qoakdgquffb0@216.10.27.159:6837/"
]

from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
FILE_NAME_FULLDUMP = os.path.join(BASE_DIR, f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_{'sample'}.txt")
EXPORT_LIMIT = 200
