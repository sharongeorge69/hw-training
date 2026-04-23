from mongoengine import Document, StringField

class ResponseURLItem(Document):
    pdp_url = StringField(required=True, unique=True)
    meta = {
        'collection': 'grainger_url',
        'indexes': ['pdp_url']
    }

class ProductDataItem(Document):
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
    url = StringField(unique=True)
    availability = StringField()
    date_crawled = StringField()
    lead_time = StringField()
    rohs_reach = StringField()
    stock_on_hand = StringField()

    meta = {
        'collection': 'grainger_data',
        'indexes': ['url']
    }
