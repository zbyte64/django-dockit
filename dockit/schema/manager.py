from copy import copy
from dockit.backends import get_document_backend

class Manager(object):
    def contribute_to_class(self, cls, name):
        new = copy(self)
        new.schema = cls
        new.collection = cls.collection
        setattr(cls, name, new)
    
    def all(self):
        backend = get_document_backend()
        return backend.all(self.schema, self.collection)
    
    def get(self, doc_id):
        backend = get_document_backend()
        data = backend.get(self.collection, doc_id)
        return self.schema.to_python(data)
    
    def filter(self, **params):
        backend = get_document_backend()
        return backend.filter(self.schema, self.collection, params)
