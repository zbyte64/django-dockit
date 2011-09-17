from pymongo import Connection
from dockit.backends import BaseDocumentStorage

from django.conf import settings

class DocumentQuery(object):
    def __init__(self, queryset, doc_class):
        self.queryset = queryset
        self.doc_class = doc_class
    
    def wrap(self, entry):
        return self.doc_class.to_python(entry)
    
    def __len__(self):
        return len(self.queryset)
    
    def count(self):
        return self.queryset.count()
    
    def __getitem__(self, val):
        if isinstance(val, slice):
            results = list()
            for entry in self.queryset[val]:
                results.append(self.wrap(entry))
            return results
        else:
            return self.wrap(self.queryset[val])

class ModelDocumentStorage(BaseDocumentStorage):

    def __init__(self):
        #TODO be proper about this
        self.connection = Connetion(settings.MONGO_HOST, settings.MONGO_PORT)
        self.db = self.connection[settings.MONGO_DB)
    
    def save(self, collection, data):
        data['_id'] = self.db[collection].insert(data)
    
    def get(self, collection, doc_id):
        return self.db[collection].find_one({'_id':doc_id})
    
    def define_index(self, collection, index):
        raise NotImplementedError
    
    def get_id(self, data):
        return str(data.get('_id'))
    
    def all(self, doc_class, collection):
        return DocumentQuery(self.db[collection], doc_class)
    
    def filter(self, doc_class, collection, params):
        qs = self.db[collection].filter(params)
        return DocumentQuery(qs, doc_class)
    
    def generate_index(self, collection, field):
        self.db[collection].ensureIndex({field:1})
   
        

