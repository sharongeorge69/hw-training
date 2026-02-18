
# basic details
PROJECT = ""
PROJECT_NAME = "jcpenney"
BASE_URL = "https://www.jcpenney.com/"
SITEMAP_URL = "https://www.jcpenney.com/m/site-map"

# Mongo db and collections
MONGO_DB = PROJECT_NAME
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_CATEGORY_NO_PRICE = f"{PROJECT_NAME}_category_url_no_price"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_SAMPLE = f"{PROJECT_NAME}_sample"
MONGO_COLLECTION_PRODUCTS = f"{PROJECT_NAME}_products"
MONGO_URI = "mongodb://localhost:27017/"

# Export settings
from datetime import datetime
FILE_NAME_FULLDUMP = f"{PROJECT_NAME}_export_{datetime.now().strftime('%Y%m%d')}.csv"
EXTRACTION_DATE = datetime.now().strftime('%Y-%m-%d')



HEADERS= {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.jcpenney.com/d/women',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}
