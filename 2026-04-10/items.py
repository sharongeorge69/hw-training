from mongoengine import DynamicDocument, StringField
import settings

class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped Mercator PDP URLs.
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
    Collection for Mercator product data.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }
    unique_id = StringField(unique=True, required=True)
    product_unique_key = StringField()
    competitor_name = StringField()
    extraction_date = StringField()
    product_name = StringField()
    brand = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    breadcrumb = StringField()
    pdp_url = StringField()
    regular_price = StringField()
    selling_price = StringField()
    price_was = StringField()
    price_per_unit = StringField()
    currency = StringField()
    product_description = StringField()
    image_url_1 = StringField()
    image_url_2 = StringField()
    image_url_3 = StringField()
    image_url_4 = StringField()
    image_url_5 = StringField()
    image_url_6 = StringField()
    promotion_description = StringField()
    site_shown_uom = StringField()
    producthierarchy_level1 = StringField()
    producthierarchy_level2 = StringField()
    producthierarchy_level3 = StringField()
    producthierarchy_level4 = StringField()
    producthierarchy_level5 = StringField()
    producthierarchy_level6 = StringField()
    producthierarchy_level7 = StringField()
