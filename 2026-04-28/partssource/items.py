from mongoengine import DynamicDocument, StringField, ListField, DictField
import settings

class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped PartsSource PDP URLs.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    pdp_url = StringField(unique=True, required=True)
    category_url = StringField()
    product_id = StringField()

class ProductDataItem(DynamicDocument):
    """
    Collection for PartsSource product data.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }
    manufacturer_name = StringField()
    brand_name = StringField()
    manufacturer_part_number = StringField()
    vendor_seller_part_number = StringField()
    item_name = StringField()
    product_overview = StringField()
    features = StringField()
    technical_spec = StringField()
    product_category = StringField()
    upc = StringField()
    country_of_origin = StringField()
    price = StringField()
    unit_of_issue = StringField()
    qty_per_uoi = StringField()
    stock_on_hand = StringField()
    lead_time = StringField()
    url = StringField(unique=True, required=True)
    availability = StringField()
    date_crawled = StringField()
