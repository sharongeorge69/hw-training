from datetime import datetime

# Basic Details
PROJECT_NAME = "reelly"
BASE_URL = "https://find.reelly.io/"
API_URL = "https://api-reelly.up.railway.app/api/internal/projects"

# Mongo DB and Collections
MONGO_DB = "reelly_db"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_COLLECTION_URLS = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_PRODUCTS = f"{PROJECT_NAME}_products"

# Export Settings
FILE_NAME_FULLDUMP = f"{PROJECT_NAME}_export_{datetime.now().strftime('%Y%m%d')}.csv"
EXTRACTION_DATE = datetime.now().strftime('%Y-%m-%d')

# Authentication
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'referer': 'https://find.reelly.io/',
    'priority': 'u=1, i',
    'xano-authorization': 'eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiemlwIjoiREVGIn0.NDcQf3hJext1QilFYJSHlLYESEm4MNFqKZVQzJ8BKqWOFxtbt33sGuLVu209_VmYf_LfqRo8mX3TU_EBr8nNBZM1cAuOrE_R.0w2eDkJY5grLxaZ3_haaJQ.crdJupv73FW7yz9DmHUqmRO_auqe7B_HLLpeIYOaFqqFToEdxI92Um6Mny6jIyp3nXqorGexw17Uci2DDyMRTjekCVb0S6AWelNDF0HQDWDr90IdWwkpgMopLX9nla24YI7ABhz-DdOYVio-qUDitA.xXr4zGEtsWIDkdehbc2idm37K0pDDqi74DjbWxWr6Ko'
}
