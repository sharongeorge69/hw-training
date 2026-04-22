from mongoengine import DynamicDocument, StringField
import settings

class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped HD Supply PDP URLs.
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
    Collection for HD Supply product data.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }
    company_name = StringField()
    manufacturer_name = StringField()
    brand_name = StringField()
    manufacturer_part_number = StringField()
    vendor_seller_part_number = StringField()
    item_name = StringField()
    full_product_description = StringField()
    price = StringField()
    country_of_origin = StringField()
    unit_of_issue = StringField()
    qty_per_uoi = StringField()
    upc = StringField()
    model_number = StringField()
    product_category = StringField()
    url = StringField(unique=True, required=True)
    availability = StringField()
    date_crawled = StringField()
    lead_time = StringField()
    rohs_reach = StringField()
    stock_on_hand = StringField()
