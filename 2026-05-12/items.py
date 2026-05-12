from mongoengine import DynamicDocument, StringField
import settings

class ProjectItem(DynamicDocument):
    """
    Collection for valid Dubailand project discovery info.
    """
    meta = {
        "db_alias": "default",
        "collection": settings.MONGO_COLLECTION_RESPONSE
    }
    project_number = StringField(unique=True, required=True)
    project_name = StringField()
    extraction_date = StringField()

