import logging
import time
import pymongo
from curl_cffi import requests
from pymongo import MongoClient
from settings import (
    MONGO_URI, MONGO_DB,
    MONGO_COLLECTION_RESPONSE,
    headers_crawler, cookies
)
from items import ResponseURLItem
# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Crawler:
    
    def __init__(self):
        self.headers = headers_crawler
        self.cookies = cookies
        
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.url_collection.create_index("pdp_url", unique=True)
        logger.info("Connected to MongoDB")

    def parse_item(self, data):
        """Processes the full API response, extracts products, validates, and saves them."""
        if self.total_found is None:
            self.total_found = data.get('productsFound', 0)
            logger.info(f"  Total products found: {self.total_found}")
        
        products = data.get('products', [])
        if not products:
            return False

        for product in products:
            art_num = product.get('commercialArticleNumber')
            pdp_url = f"https://www.colruyt.be/nl/producten/{art_num}" if art_num else None
            
            if not pdp_url:
                continue

            retailProductNumber = product.get('retailProductNumber')
            name = product.get('name')
            brand = product.get('brand')
            seoBrand = product.get('seoBrand')
            thumbNail = product.get('thumbNail')
            fullImage = product.get('fullImage')
            content = product.get('content')
            price = product.get('price')

            if isinstance(price, dict):
                basicPrice = price.get('basicPrice')
                recommendedQuantity = price.get('recommendedQuantity')
                quantityPrice = price.get('quantityPrice') if price.get('quantityPrice') else ""
                quantityPriceQuantity = price.get('quantityPriceQuantity') if price.get('quantityPriceQuantity') else ""
                measurementUnitQuantityPrice = price.get('measurementUnitQuantityPrice') if price.get('measurementUnitQuantityPrice') else ""
                measurementUnitPrice = price.get('measurementUnitPrice')
                measurementUnit = price.get('measurementUnit')
                pricePerUOM = price.get('pricePerUOM')
            else:
                basicPrice = recommendedQuantity = quantityPrice = quantityPriceQuantity = ""
                measurementUnitQuantityPrice = measurementUnitPrice = measurementUnit = pricePerUOM = ""

            isAvailable = product.get('isAvailable')
            countryOfOrigin = product.get('countryOfOrigin')
            
            promotion = product.get('promotion')
            if isinstance(promotion, list) and len(promotion) > 0:
                promotion = promotion[0]
            
            if isinstance(promotion, dict):
                techPromoId = promotion.get('techPromoId') or ""
                promotionId = promotion.get('promotionId') or ""
                promotionType = promotion.get('promotionType') or ""
                publicationStartDate = promotion.get('publicationStartDate') or ""
                publicationEndDate = promotion.get('publicationEndDate') or ""
            else:
                techPromoId = promotionId = promotionType = publicationStartDate = publicationEndDate = ""

            # Processing and standardization
            technicalArticleNumber = str(product.get('technicalArticleNumber', ""))
            commercialArticleNumber = str(art_num) if art_num is not None else ""
            retailProductNumber = str(retailProductNumber) if retailProductNumber is not None else ""
            name = str(name) if name is not None else ""
            brand = str(brand) if brand is not None else ""
            seoBrand = str(seoBrand) if seoBrand is not None else ""
            thumbNail = str(thumbNail) if thumbNail is not None else ""
            fullImage = str(fullImage) if fullImage is not None else ""
            content = str(content) if content is not None else ""
            basicPrice = str(basicPrice) if basicPrice is not None and basicPrice != "" else ""
            recommendedQuantity = str(recommendedQuantity) if recommendedQuantity is not None and recommendedQuantity != "" else ""
            quantityPrice = str(quantityPrice) if quantityPrice is not None and quantityPrice != "" else ""
            quantityPriceQuantity = str(quantityPriceQuantity) if quantityPriceQuantity is not None and quantityPriceQuantity != "" else ""
            measurementUnitQuantityPrice = str(measurementUnitQuantityPrice) if measurementUnitQuantityPrice is not None and measurementUnitQuantityPrice != "" else ""
            measurementUnitPrice = str(measurementUnitPrice) if measurementUnitPrice is not None and measurementUnitPrice != "" else ""
            measurementUnit = str(measurementUnit) if measurementUnit is not None and measurementUnit != "" else ""
            pricePerUOM = str(pricePerUOM) if pricePerUOM is not None and pricePerUOM != "" else ""
            isAvailable = str(isAvailable) if isAvailable is not None else ""
            countryOfOrigin = str(countryOfOrigin) if countryOfOrigin is not None else ""
            techPromoId = str(techPromoId) if techPromoId != "" else ""
            promotionId = str(promotionId) if promotionId != "" else ""
            promotionType = str(promotionType) if promotionType != "" else ""
            publicationStartDate = str(publicationStartDate) if publicationStartDate != "" else ""
            publicationEndDate = str(publicationEndDate) if publicationEndDate != "" else ""

            item = {}
            item['pdp_url'] = pdp_url
            item['technicalArticleNumber'] = technicalArticleNumber
            item['commercialArticleNumber'] = commercialArticleNumber
            item['retailProductNumber'] = retailProductNumber
            item['name'] = name
            item['brand'] = brand
            item['seoBrand'] = seoBrand
            item['thumbNail'] = thumbNail
            item['fullImage'] = fullImage
            item['content'] = content
            item['basicPrice'] = basicPrice
            item['recommendedQuantity'] = recommendedQuantity
            item['quantityPrice'] = quantityPrice
            item['quantityPriceQuantity'] = quantityPriceQuantity
            item['measurementUnitQuantityPrice'] = measurementUnitQuantityPrice
            item['measurementUnitPrice'] = measurementUnitPrice
            item['measurementUnit'] = measurementUnit
            item['pricePerUOM'] = pricePerUOM
            item['isAvailable'] = isAvailable
            item['countryOfOrigin'] = countryOfOrigin
            item['techPromoId'] = techPromoId
            item['promotionId'] = promotionId
            item['promotionType'] = promotionType
            item['publicationStartDate'] = publicationStartDate
            item['publicationEndDate'] = publicationEndDate

            try:
                response_item = ResponseURLItem(**item)
                response_item.validate()
                self.url_collection.insert_one(item)
                logger.info(f"    Saved: {item['pdp_url']}")
            except pymongo.errors.DuplicateKeyError:
                logger.debug(f"    Skipped duplicate: {item['pdp_url']}")
            except Exception as e:
                logger.error(f"    Save error for {item.get('pdp_url')}: {e}")
        
        return True

    def start(self):
        base_url = "https://apip.colruyt.be/gateway/emec.colruyt.protected.bffsvc/cg/nl/api/product-search-prs"
        skip = 0
        self.total_found = None
        page_size = 22
        max_retries = 3

        while self.total_found is None or skip < self.total_found:
            params = {
                'placeId': 604,
                'skip': skip,
                'size': page_size,
                'sort': 'relevancy asc',
                'isAvailable': 'true',
                'categoryIds': 372
            }
            
            data = None
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        base_url,
                        params=params,
                        headers=self.headers,
                        cookies=self.cookies,
                        impersonate="chrome120",
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            break
                        except ValueError as e:
                            logger.error(f"  JSON decode error on attempt {attempt + 1}: {e}")
                    else:
                        logger.error(f"  Request failed [{response.status_code}] on attempt {attempt + 1}")
                
                except (requests.errors.Timeout, requests.errors.RequestError) as e:
                    logger.warning(f"  Retryable error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error("  Max retries reached. Skipping this page.")


            if not self.parse_item(data):
                break
            
            skip += page_size 
            time.sleep(1)  


    def close(self):

        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except:
            pass


if __name__ == "__main__":
    crawler_obj = Crawler()
    try:
        crawler_obj.start()
    finally:
        crawler_obj.close()
