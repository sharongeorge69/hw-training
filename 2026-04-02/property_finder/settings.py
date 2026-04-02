import os
from datetime import datetime

PROJECT_NAME = "property_finder"
BASE_URL = "https://www.propertyfinder.ae"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_location"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
# MONGO_URI = "mongodb://127.0.0.1:27017/"
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"


# API Headers
HEADERS = {
    'sec-ch-ua-platform': '"Linux"',
    'Referer': 'https://www.propertyfinder.ae/en/transactions/rent/dubai?period=3y',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'locale': 'en',
    'sec-ch-ua-mobile': '?0',
}

# API Params
PARAMS = {
    'l_t': 'TOWER,SUBCOMMUNITY,COMMUNITY',
    'c': '1',
    'locale': 'en',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")

# Slicing Filters
SLICER_PROPERTY_TYPES = [1, 35, 45] # Apartment, Villa, Hotel
SLICER_BEDROOMS = [0, 1, 2, 3, 4, 5, 6, 7, 8]
SLICER_PRICES = [20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 190000, 200000, 225000, 250000, 275000, 300000, 350000, 400000, 500000, 750000, 1000000]
SLICER_AREAS = [500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800, 4200, 4600, 5000, 5400, 5800, 6200, 6600, 7000, 7400, 7800, 8200, 9000]

# Export config
FILE_NAME_FULLDUMP = os.path.join(BASE_DIR, f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_sample.csv")
EXPORT_LIMIT = 200
