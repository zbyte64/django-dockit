from dockit import schema

class SimpleSchema(schema.Schema): #TODO make a more complex testcase
    charfield = schema.CharField()

class SimpleDocument(schema.Document): #TODO make a more complex testcase
    charfield = schema.CharField()
