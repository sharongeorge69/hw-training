# style_union_settings.py

# Network Settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Request Settings
TIMEOUT = 20
RETRY_COUNT = 3
INITIAL_DELAY = 5

# MongoDB Settings
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "style_union"
COLLECTION_CATEGORY = "style_union_category"
COLLECTION_PRODUCT_URLS = "style_union_product_urls"
COLLECTION_PRODUCTS = "style_union_products"

# App Settings
BASE_URL = "https://styleunion.in/"
