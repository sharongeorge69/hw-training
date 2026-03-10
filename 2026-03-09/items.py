from mongoengine import DynamicDocument, StringField
import settings


class ProductDataItem(DynamicDocument):
    """
    Collection for scraped eReplacementParts product data.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }

    input_part_number = StringField(unique=True)
    url = StringField()
    title = StringField()
    manufacturer = StringField()
    price = StringField()
    description = StringField()
    oem_part_number = StringField()
    retailer_part_number = StringField()
    competitor_part_numbers = StringField()
    compatible_products = StringField()
    equivalent_part_numbers = StringField()
    product_specifications = StringField()
    additional_description = StringField()
    availability = StringField()
    image_urls = StringField()
    linked_files = StringField()


class CategoryItem(DynamicDocument):
    """
    Collection for scraped eReplacementParts category URLs.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_CATEGORY
    }

    category_url = StringField(unique=True)


class ResponseURLItem(DynamicDocument):
    """
    Collection for scraped eReplacementParts PDP URLs.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }

    pdp_url = StringField(unique=True)
