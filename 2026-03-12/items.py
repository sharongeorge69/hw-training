from mongoengine import DynamicDocument, StringField, FloatField, BooleanField
import settings

class ProductDataItem(DynamicDocument):
    """
    Collection for final parsed Colruyt product data.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }

    unique_id = StringField(unique=True, required=True)
    pdp_url = StringField(required=True)
    competitor_name = StringField()
    extraction_date = StringField()
    product_name = StringField()
    brand = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    breadcrumb = StringField()
    # Product hierarchy levels
    producthierarchy_level1 = StringField()
    producthierarchy_level2 = StringField()
    producthierarchy_level3 = StringField()
    producthierarchy_level4 = StringField()
    producthierarchy_level5 = StringField()
    producthierarchy_level6 = StringField()
    producthierarchy_level7 = StringField()
    regular_price = StringField()
    selling_price = StringField()
    promotion_valid_from = StringField()
    promotion_valid_upto = StringField()
    price_valid_from = StringField()
    price_per_unit = StringField()
    image_url_1 = StringField()
    file_name_1 = StringField()
    allergens = StringField()
    promotion_description = StringField()
    currency = StringField()
    site_shown_uom = StringField()
    instock = StringField()
    product_unique_key = StringField()
    product_description = StringField()
    country_of_origin = StringField()

    # Crawler payload fields
    measurementUnitQuantityPrice = StringField()
    measurementUnitPrice = StringField()
    measurementUnit = StringField()
    pricePerUOM = StringField()
    techPromoId = StringField()
    promotionId = StringField()
    # Product Details API payload fields (Dynamic to handle arbitrary JSON for now)
    product_details = StringField()
    
    # Promotion API payload fields
    promotion_details = StringField()

class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped Colruyt PDP URLs.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }

    pdp_url = StringField(unique=True, required=True)
    technicalArticleNumber = StringField()
    commercialArticleNumber = StringField()
    retailProductNumber = StringField()
    name = StringField()
    brand = StringField()
    seoBrand = StringField()
    thumbNail = StringField()
    fullImage = StringField()
    content = StringField()
    basicPrice = StringField()
    recommendedQuantity = StringField()
    quantityPrice = StringField()
    quantityPriceQuantity = StringField()
    measurementUnitQuantityPrice = StringField()
    measurementUnitPrice = StringField()
    measurementUnit = StringField()
    pricePerUOM = StringField()
    isAvailable = StringField()
    countryOfOrigin = StringField()
    techPromoId = StringField()
    promotionId = StringField()
    promotionType = StringField()
    publicationStartDate = StringField()
    publicationEndDate = StringField()
