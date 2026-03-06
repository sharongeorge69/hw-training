# settings.py
PROJECT_NAME = "ereplacementparts"
BASE_URL = "https://www.ereplacementparts.com"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"

MONGO_URI = "mongodb://localhost:27017/"

headers_crawler = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9',
}