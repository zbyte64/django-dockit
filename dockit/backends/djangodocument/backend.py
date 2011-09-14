from django.utils import simplejson
from django.db.models import Model

from dockit.backends.base import BaseDocumentStorage
from dockit.schema import fields, Document

from models import DocumentStore, StringIndex, IntegerIndex

class ListIndex(object):
    def __init__(self, index_func):
        self.index_func = index_func
    
    def __call__(self, documentstore, name, value):
        for val in value:
            self.index_func(documentstore, name, value)

class ModelDocumentStorage(BaseDocumentStorage):
    INDEXES = [(fields.TextField, StringIndex),
           (fields.IntegerField, IntegerIndex),
           #(fields.SchemaField, TextIndex), #unsoported
           #(fields.ListField, None), #multi key index
           #(fields.DictField, None), #multi key index
           (Document, StringIndex),
           (Model, StringIndex),
           (fields.ReferenceField, StringIndex),
           (fields.ModelReferenceField, StringIndex),]
    
    def __init__(self):
        self.indexes = dict()
    
    def save(self, collection, data):
        doc_id = self.get_id(data)
        document = DocumentStore(collection=collection, data=simplejson.dumps(data))
        if doc_id is not None:
            document.pk = doc_id
        #CONSIDER this does not look before we save
        document.save()
        data['_pk'] = document.pk
        self.update_indexes(document, collection, data)
    
    def get(self, collection, doc_id):
        try:
            document = DocumentStore.objects.get(collection=collection, pk=doc_id)
        except DocumentStore.DoesNotExist:
            raise #TODO raise proper error
        data = simplejson.loads(document.data)
        data['_pk'] = document.pk
        return data
    
    def define_index(self, collection, index):
        raise NotImplementedError
    
    def get_id(self, data):
        return data.get('_pk')
    
    def all(self, doc_class, collection):
        qs = DocumentStore.objects.filter(collection=collection)
        
        def entry_to_document(entry):
            data = simplejson.loads(entry.data)
            data['_pk'] = entry.pk
            return doc_class.to_python(data)
        
        def result_set():
            for entry in qs:
                yield entry_to_document(entry)
        
        return list(result_set())
    
    def filter(self, doc_class, collection, params):
        pass
    
    def generate_index(self, collection, field):
        #TODO create a better interface
        self.indexes.setdefault(collection, list())
        if isinstance(field, fields.ListField):
            subindex = self._lookup_index(field.schema)
            func = ListIndex(subindex.objects.db_index)
        else:
            index = self._lookup_index(field)
            func = index.objects.db_index
        self.indexes[collection].append(field.name, func)
    
    def _lookup_index(field):
        for key, val in self.INDEXES:
            if isinstance(field, key):
                return val
    
    def update_indexes(self, document, collection, data):
        document.clear_indexes()
        for field_name, index_func in self.indexes.get(collection, []):
            if field_name in data:
                index_func(document, field_name, data[field_name])
        

