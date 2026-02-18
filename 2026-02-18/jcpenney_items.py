from mongoengine import Document, DynamicDocument, StringField, ListField
import jcpenney_settings as settings

class ProductItem(Document):
    """
    JCPenney Product Item following MongoEngine DynamicDocument structure
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_PRODUCTS
    }

    # Define common fields to ensure types
    unique_id = StringField()
    url = StringField(unique=True)
    product_name = StringField()
    brand = StringField()
    selling_price = StringField()
    regular_price = StringField()
    discount = StringField()
    description = StringField()
    specification = StringField()
    fit_type = StringField()
    image = StringField()
    rating = StringField()
    review = StringField()
    size = StringField()
    colour = StringField()

class ProductUrlItem(DynamicDocument):
    """
    Collection for discovered product URLs
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    
    product_url = StringField(unique=True)
    categories = ListField() # List of category objects/names
