from dockit import schema

class ImageEntry(schema.Schema):
    caption = schema.CharField()
    image = schema.ImageField(upload_to='images')

class SimpleSchema(schema.Schema): #TODO make a more complex testcase
    charfield = schema.CharField()
    gallery = schema.ListField(schema.SchemaField(ImageEntry))

class SimpleDocument(schema.Document): #TODO make a more complex testcase
    charfield = schema.CharField()
    complex_list = schema.ListField(schema.SchemaField(SimpleSchema))

