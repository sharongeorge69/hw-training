import os
from datetime import datetime

PROJECT_NAME = "mscdirect"
BASE_URL = "https://www.mscdirect.com"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

# Target URLs to scrape (no crawler, direct list)
TARGET_URLS = [
    "https://www.mscdirect.com/product/details/44533321?orderedAs=JD44533321&pxno=87486433",
    "https://www.mscdirect.com/product/details/88117221?orderedAs=JD88117221&pxno=87486434",
    "https://www.mscdirect.com/product/details/37285467?orderedAs=JD37285467&pxno=87486461",
    "https://www.mscdirect.com/product/details/89836522?orderedAs=JD89836522&pxno=87486438",
    "https://www.mscdirect.com/product/details/59828996?orderedAs=JD59828996&pxno=87486435",
    "https://www.mscdirect.com/product/details/45645991?orderedAs=JD45645991&pxno=87486463",
    "https://www.mscdirect.com/product/details/05751003?orderedAs=JD05751003&pxno=87486418",
    "https://www.mscdirect.com/product/details/41028416?orderedAs=JD41028416&pxno=87486415",
    "https://www.mscdirect.com/product/details/72761778?orderedAs=JD72761778&pxno=87486405",
    "https://www.mscdirect.com/product/details/71939086?orderedAs=JD71939086&pxno=87486437",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
