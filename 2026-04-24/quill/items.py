from mongoengine import DynamicDocument, StringField, DictField
import settings

class ProductDataItem(DynamicDocument):
    """
    Collection for Quill product data.
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
    model_number = StringField()
    item_name = StringField()
    full_product_description = StringField()
    price = StringField()
    unit_of_issue = StringField()
    qty_per_uoi = StringField()
    product_category = StringField()
    url = StringField(unique=True, required=True)
    availability = StringField()
    date_crawled = StringField()
    full_product_description_2 = DictField()
    lead_time = StringField()
    rohs_reach = StringField()
    stock_on_hand = StringField()
    upc = StringField()
    country_of_origin = StringField()
