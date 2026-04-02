from mongoengine import DynamicDocument, StringField
import settings

class LocationItem(DynamicDocument):
    """
    Collection for Property Finder locations.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    n = StringField(required=True)     
    l_t = StringField()             
    s = StringField(unique=True)
    en_s = StringField()            
    extraction_date = StringField()

class TransactionItem(DynamicDocument):
    """
    Collection for Property Finder transactions.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA
    }
    unique_id = StringField(unique=True, required=True)
    category = StringField()
    contract_start_date = StringField()
    contract_end_date = StringField()
    property_size = StringField()
    bedrooms = StringField()
    location = StringField()
    price = StringField()
    property_type = StringField()
    status = StringField()
    transaction_date = StringField()
    property_number = StringField()
    price_per_sqft = StringField()
    extraction_date = StringField()
