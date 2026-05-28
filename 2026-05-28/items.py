from mongoengine import DynamicDocument, StringField, DictField, ListField
import settings

class ResponseURLItem(DynamicDocument):
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    product_url = StringField(unique=True, required=True)
    product_id = StringField()
    category_url = StringField()
    category_name = StringField()
    product_name = StringField()
    brand = StringField()
    sku_code = StringField()
    taxonomy = StringField()
    grammage = StringField()
    selling_price = StringField()
    mrp = StringField()
    main_image_url = StringField()
    image_urls = ListField(StringField())
    seller_id = StringField()
    country_of_origin = StringField()
    extraction_date = StringField()
