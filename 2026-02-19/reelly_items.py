from mongoengine import FloatField
from mongoengine import Document, DynamicDocument, StringField, IntField
import reelly_settings as settings

class ProductUrlItem(DynamicDocument):
   #Collection for discovered project URLs/IDs
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    
    project_id = IntField(required=True, unique=True)
    name = StringField()
    url = StringField()
    api_url = StringField()

class ProductItem(Document):
    """
    Reelly Product Item Schema
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_DATA,
        "strict": False 
    }

    project_id = IntField(required=True, unique=True)
    name = StringField()
    construction_start_date = StringField()
    construction_end_date = StringField()
    developer_name = StringField()
    main_office = StringField()
    description = StringField()
    amenities = StringField()
    furnishing = StringField()
    service_charge = StringField()
    resale_conditions = StringField()
    unit_types = StringField()
    price_from = FloatField()
    district = StringField()
    cover_image_url = StringField()
    floors = StringField()
    url = StringField()
