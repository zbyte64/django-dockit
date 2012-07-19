from dockit import schema

from django.contrib.contenttypes.models import ContentType

class ChildDocument(schema.Document):
    charfield = schema.CharField()
    
    def create_natural_key(self):
        return {'charfield': self.charfield}

class ChildSchema(schema.Schema):
    ct = schema.ModelReferenceField(ContentType)

class ParentDocument(schema.Document):
    title = schema.CharField()
    subdocument = schema.ReferenceField(ChildDocument)
    subschema = schema.SchemaField(ChildSchema)
