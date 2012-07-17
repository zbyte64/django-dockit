from dockit import schema

class ChildDocument(schema.Document):
    charfield = schema.CharField()
    
    def create_natural_key(self):
        return {'charfield': self.charfield}

class ParentDocument(schema.Document):
    title = schema.CharField()
    subdocument = schema.ReferenceField(ChildDocument)
