
# basic details
PROJECT = ""
PROJECT_NAME = "aldi"
BASE_URL = "https://www.aldi.us/"


# Mongo db and collections
MONGO_DB = PROJECT_NAME
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_CATEGORY_PLAYWRIGHT = f"{PROJECT_NAME}_category_url_playwright"
MONGO_COLLECTION_CATEGORY_CLOUDSCRAPER = f"{PROJECT_NAME}_category_url_cloudscraper"
MONGO_COLLECTION_CATEGORY_CURL = f"{PROJECT_NAME}_category_url_curl"


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

SITEMAP_URL = "https://www.aldi.us/sitemap.html"