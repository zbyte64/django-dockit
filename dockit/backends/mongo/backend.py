from pymongo import Connection
from dockit.backends.base import BaseDocumentStorage, BaseDocumentQuerySet

from django.conf import settings

class DocumentQuery(BaseDocumentQuerySet):
    def __init__(self, queryset, doc_class):
        self.queryset = queryset
        self.doc_class = doc_class
        super(DocumentQuery, self).__init__()
    
    def wrap(self, entry):
        return self.doc_class.to_python(entry)
    
    def __len__(self):
        return len(self.queryset)
    
    def __nonzero__(self):
        return bool(self.queryset)
    
    def __getitem__(self, val):
        if isinstance(val, slice):
            results = list()
            for entry in self.queryset[val]:
                results.append(self.wrap(entry))
            return results
        else:
            return self.wrap(self.queryset[val])
    
    #TODO and & or operations

class MongoDocumentStorage(BaseDocumentStorage):

    def __init__(self):
        #TODO be proper about this
        self.connection = Connection(settings.MONGO_HOST, settings.MONGO_PORT)
        self.db = self.connection[settings.MONGO_DB]
    
    def save(self, doc_class, collection, data):
        data['_id'] = self.db[collection].insert(data)
    
    def get(self, doc_class, collection, doc_id):
        return self.db[collection].find_one({'_id':doc_id})
    
    def delete(self, doc_class, collection, doc_id):
        return self.db[collection].remove(doc_id)
    
    def get_id_field_name(self):
        return '_id'
    
    def all(self, doc_class, collection):
        return DocumentQuery(self.db[collection], doc_class)
    
    def filter(self, doc_class, collection, params):
        qs = self.db[collection].filter(params)
        return DocumentQuery(qs, doc_class)
    
    #def generate_index(self, collection, dotpath):
    #    self.db[collection].ensureIndex({dotpath:1})

