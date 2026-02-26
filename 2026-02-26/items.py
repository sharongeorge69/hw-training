from mongoengine import Document, DynamicDocument, StringField, ListField, FloatField
import settings

class ProductUrlItem(DynamicDocument):
    """
    Collection for discovered product URLs
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    
    unique_id = StringField(unique=True)
    pdp_url = StringField()
    product_name = StringField()
    brand = StringField()
    selling_price = FloatField()
    percentage_discount = FloatField()
    image_url = StringField()
    seller_name = StringField()
