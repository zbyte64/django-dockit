import dockit

class TemporarySchemaStorage(dockit.Document):
    schema_identifier = dockit.TextField()
    data = dockit.DictField()
