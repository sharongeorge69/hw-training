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

class ProductDataItem(DynamicDocument):
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }
    product_url = StringField(unique=True, required=True)
    product_id = StringField()
    product_name = StringField()
    brand = StringField()
    taxonomy = StringField()
    category_name = StringField()
    selling_price = StringField()
    mrp = StringField()
    discount_percentage = StringField()
    promotion_description = StringField()
    product_rating = StringField()
    product_availability = StringField()
    stock_count = StringField()
    product_description = StringField()
    instructions = StringField()
    storage_instructions = StringField()
    main_image_url = StringField()
    image_urls = ListField(StringField())
    highlights = StringField()
    pincode = StringField()
    store_id = StringField()
    extraction_datetime = StringField()
    specification = ListField(DictField())
