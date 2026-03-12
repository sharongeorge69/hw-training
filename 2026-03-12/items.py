from mongoengine import DynamicDocument, StringField, FloatField
import settings

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
