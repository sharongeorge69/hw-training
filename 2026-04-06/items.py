from mongoengine import DynamicDocument, StringField
import settings

class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped Moglix PDP URLs.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    pdp_url = StringField(unique=True, required=True)
    category_name = StringField()
    category_url = StringField()
