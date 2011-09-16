import dockit

class SchemaFragment(dockit.Document):
    identifier = dockit.TextField()
    data = dockit.DictField()
