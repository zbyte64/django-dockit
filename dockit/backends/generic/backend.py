from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

from dockit.backends.base import BaseDocumentStorage
#from dockit.backends.queryset import BaseDocumentQuery

class GenericDocumentStorage(BaseDocumentStorage):
    name = "generic"
    
    def __init__(self, key_value_backend=None, map_reduce_backend=None, **kwargs):
        self.key_value_backend = key_value_backend
        self.map_reduce_backend = map_reduce_backend
    
    def get_id_field_name(self):
        return self.key_balue_backend.get_id_field_name()
    
    def save(self, doc_class, collection, data):
        doc_id = self.get_id(data)
        encoded_data = simplejson.dumps(data, cls=DjangoJSONEncoder)
        
        self.key_value_backend.save(collection, doc_id, data, encoded_data)
        self.map_reduce_backend.on_save(collection, doc_id, data, encoded_data)
    
    def get(self, doc_class, collection, doc_id):
        try:
            data = self.key_value_backend.get(collection, doc_id)
        except KeyError: #TODO proper exception
            raise doc_class.DoesNotExist
        return data
    
    def delete(self, doc_class, collection, doc_id):
        self.key_value_backend.delete(collection, doc_id)
        self.map_reduce_backend.on_delete(collection, doc_id)
    
    def register_index(self, query_index):
        self.map_reduce_backend.register_index(query_index)
    
    def remove_index(self, query_index):
        self.map_reduce_backend.remove_index(query_index)
    
    def get_query(self, query_index):
        return self.map_reduce_backend.get_query(query_index)


class BaseKeyValueBackend(object):
    def get_id_field_name(self):
        return '_pk'
    
    def save(self, collection, doc_id, data, encoded_data):
        raise NotImplementedError
    
    def get(self, collection, doc_id):
        raise NotImplementedError
    
    def delete(self, collection, doc_id):
        raise NotImplementedError

class BaseMapReduceBackend(object):
    def on_save(self, collection, doc_id, data, encoded_data):
        raise NotImplementedError
    
    def on_delete(self, collection, doc_id):
        raise NotImplementedError
    
    def register_index(self, query_index):
        raise NotImplementedError
    
    def remove_index(self, query_index):
        raise NotImplementedError
    
    def get_query(self, query_index):
        raise NotImplementedError

