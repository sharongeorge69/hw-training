from mongoengine import DynamicDocument, StringField, FloatField, BooleanField
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
    category_url = StringField()
    product_id = StringField()