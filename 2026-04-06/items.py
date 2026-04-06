from mongoengine import DynamicDocument, StringField
from settings import MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA

class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped Moglix PDP URLs.
    """
    meta = {
        "db_alias": "default",
        "collection": MONGO_COLLECTION_RESPONSE
    }
    pdp_url = StringField(unique=True, required=True)
    category_name = StringField()
    category_url = StringField()

class ProductDataItem(DynamicDocument):
    """
    Collection for Moglix product data.
    """
    meta = {
        "db_alias": "default",
        "collection": MONGO_COLLECTION_DATA
    }
    product_page_url = StringField(unique=True, required=True)
    product_name = StringField()
    product_specifications = StringField()  
    product_description = StringField()
    product_features = StringField()
    product_image_url = StringField()
    product_video_url = StringField()
