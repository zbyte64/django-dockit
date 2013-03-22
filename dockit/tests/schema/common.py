from dockit import schema

class SimpleSchema(schema.Schema): #TODO make a more complex testcase
    charfield = schema.CharField()

class SimpleSchema2(schema.Schema):
    otherfield = schema.CharField()

class SimpleDocument(schema.Document): #TODO make a more complex testcase
    charfield = schema.CharField()

class ValidatingDocument(schema.Document):
    with_choices = schema.CharField(choices=[('a','a'), ('b', 'b')])
    not_null = schema.CharField(null=False)
    allow_blank = schema.CharField(blank=True)
    not_blank = schema.CharField(blank=False)
    subschema = schema.SchemaField(SimpleSchema, null=False)
    allow_null = schema.CharField(blank=True, null=True)
