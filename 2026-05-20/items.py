from mongoengine import (
    DynamicDocument,
    StringField,
    IntField,
    BooleanField,
    ListField,
    DictField,
)
import settings

class ProductDataItem(DynamicDocument):
    """Collection for Blinkit product data."""

    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA,
    }

    # Identity
    unique_id   = StringField(unique=True, required=True)
    group_id    = StringField(default="")
    product_url = StringField(default="")

    # Product info
    product_name  = StringField(default="")
    brand         = StringField(default="")
    grammage      = StringField(default="")
    product_description = StringField(default="")
    instructions        = StringField(default="")
    storage_instructions = StringField(default="")

    # Categorisation
    breadcrumbs   = ListField(StringField(), default=list)
    category_name = StringField(default="")
    category_rank = IntField(default=None)

    # Pricing
    selling_price         = StringField(default="")
    regular_price         = StringField(default="")
    discount_percentage   = StringField(default="")
    promotion_description = StringField(default="")

    # Availability
    product_availability = StringField(default="")
    is_sold_out          = BooleanField(default=False)
    stock_quantity       = IntField(default=0)
    product_rating       = StringField(default="")

    # Store & seller
    store_id       = StringField(default="")
    seller_details = StringField(default="")

    # Media
    image_urls     = ListField(StringField(), default=list)
    main_image_url = StringField(default="")

    # Details & relations
    highlights                = DictField(default=dict)
    additional_product_details = DictField(default=dict)

    # Crawl metadata
    extraction_datetime = StringField(default="")
    page_depth          = IntField(default=None)
    listing_type        = StringField(default="")

    # Raw response storage
    response = DictField(default=dict)
    meta_data = DictField(default=dict)