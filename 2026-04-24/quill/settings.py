import os
from datetime import datetime

PROJECT_NAME = "quill"

# MongoDB Settings
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"
MONGO_DB = f"{PROJECT_NAME}_db"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"

# Extraction Date
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")

# List of URLs to parse
TARGET_URLS = [
    "https://www.quill.com/duracell-coppertop-aa-alkaline-batteries-36-pack-mn15p36/cbs/54803327.html?Effort_Code=032&Find_Number=464050",
    "https://www.quill.com/quill-brand-standard-1-3-ring-view-binder-3-ring-white-24-pack/cbs/55480466.html?Effort_Code=032&Find_Number=CD7221WE4",
    "https://www.quill.com/glad-drawstring-13-gallon-tall-trash-bags-71-mil-2374-x-254-light-gray-100-bags-box-clo-78526/cbs/055376.html?Effort_Code=032&Find_Number=61024",
    "https://www.quill.com/sharpie-permanent-markers-fine-point-black-36-pack-1884739/cbs/50810015.html?Effort_Code=032&Find_Number=271674",
    "https://www.quill.com/folgers-classic-roast-ground-coffee-medium-roast-403-oz-2550030419/cbs/54698152.html",
    "https://www.quill.com/post-it-notes-3-x-3-canary-yellow-100-sheets-pad-12-pads-pack-654-12yw/cbs/006350.html?Effort_Code=032&Find_Number=654YW",
    "https://www.quill.com/dawn-ultra-ez-squeeze-dish-soap-22-oz-3-pack-scotch-brite-non-scratch-scrub-sponge-3-pack/cbs/55457709.html",
    "https://www.quill.com/staples-electronics-air-duster-10-oz-2-pack-spl10enfr-2/cbs/55460685.html",
    "https://www.quill.com/scotch-heavy-duty-shipping-packing-tape-dispenser-188w-x-22-yds-clear-6-rolls-142-6/cbs/055902.html",
    "https://www.quill.com/quill-brand-standard-manila-file-folders-1-ply-1-3-cut-assorted-tabs-letter-size-100-bx/cbs/002372.html?Effort_Code=032&Find_Number=740137"
]


HEADERS = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.quill.com/',
            'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
        }