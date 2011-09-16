import dockit

class TemporarySchemaStorage(dockit.Document):
    identifier = dockit.TextField()
    data = dockit.DictField()
