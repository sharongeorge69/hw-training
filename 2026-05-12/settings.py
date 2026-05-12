PROJECT_NAME = "dubailand"
BASE_URL = "https://b2c.dubailand.gov.ae"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

# MONGO_URI = "mongodb://127.0.0.1:27017/"
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

# User requested range
PROJECT_NUMBER = list(range(1500, 1700)) 


CONSUMER_ID = 'gkb3WvEG0rY9eilwXC0P2pTz8UzvLj9F'

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'consumer-id': CONSUMER_ID,
    'content-type': 'application/json; charset=utf-8',
    'origin': 'https://dubailand.gov.ae',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'token': '4Z+3Qu3asUNSj14wELmfxbKRSZLg1WYfHIF7SSAoj8mIX2O/xoqAcupjEQy1jNg1XmR6pN+m/dMILePRILdBXinc68blEKdAl6vlIsuCY9LExwQhxp3tx64VTFIwN4mZxtr+qdhf8vSzfZGIdOqgdsUlJkblIB3caCZLLKTBN16zYOs36tDcYBRy31hrg9BEFYSEvSDRqmxvlZoI9qZuBPMU7MqBvMbwsbI1UBVBUrruCkvJNH/fU9++K5GqZyWVwNxJLTEZY2sCWYwLXWCuCwnhsowNTXmSs9w7gx4LPf7tpePzAv3y0RQaPGvtYWtH29i0PAdEvHGIGM6cA9gnbL+Ua6WUvjmfWpiSoSW3a4uRj/NgWdWj/MkjETOhP7/ZydmPSOGjIFzPq9y4/rpuAVFlHtEEIkjo9BecA1Hzkj2I4YmQzgyfiTKP/aWDCqjHFBXv1ti7+WLPq9y4/rpuAdbZXopS0SHfxwUbcR5JIKDwfO+e/OsGEhVD0qBbVIx5',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
}

headers_mollak = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'origin': 'https://dubailand.gov.ae',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
}

from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
