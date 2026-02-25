from mongoengine import Document, DynamicDocument, StringField, ListField, FloatField
import settings

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
    productname = StringField()
    brand = StringField()
    selling_price = FloatField()
    regular_price = FloatField()
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

class CategoryItem(Document):
    """
    JCPenney Category Item following MongoEngine DynamicDocument structure
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_CATEGORY
    }

    url = StringField(unique=True)
    main_category_name = StringField()
    subcategory_name = StringField()
    category_id = StringField()
    api_url = StringField()
