import dockit

class SchemaFragment(dockit.Document):
    identifier = dockit.TextField()
    data = dockit.DictField()

class TemporaryDocument(dockit.Document):
    #user
    data = dockit.DictField()
