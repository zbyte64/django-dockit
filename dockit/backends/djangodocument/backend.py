from django.utils import simplejson
from django.db.models import Model

from dockit.backends.base import BaseDocumentStorage
from dockit.schema import fields#, Document

from models import DocumentStore, StringIndex, IntegerIndex

class ListIndex(object):
    def __init__(self, index_func):
        self.index_func = index_func
    
    def __call__(self, documentstore, name, value):
        for val in value:
            self.index_func(documentstore, name, val)

class DocumentQuery(object):
    def __init__(self, queryset, doc_class):
        self.queryset = queryset
        self.doc_class = doc_class
    
    def wrap(self, entry):
        data = simplejson.loads(entry.data)
        data['_pk'] = entry.pk
        return self.doc_class.to_python(data)
    
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
    INDEXES = [(fields.TextField, StringIndex),
           (fields.IntegerField, IntegerIndex),
           #(fields.SchemaField, TextIndex), #unsoported
           #(fields.ListField, None), #multi key index
           #(fields.DictField, None), #multi key index
           #(Document, StringIndex),
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
        return DocumentQuery(qs, doc_class)
    
    def filter(self, doc_class, collection, params):
        qs = DocumentStore.objects.filter(collection=collection)
        for key, value in params.iteritems():
            qs = qs.filter(**self.indexes[collection][key]['filter'](key, value))
        return DocumentQuery(qs, doc_class)
    
    def generate_index(self, collection, field):
        #TODO create a better interface
        self.indexes.setdefault(collection, dict())
        if isinstance(field, fields.ListField):
            subindex = self._lookup_index(field.schema)
            func = ListIndex(subindex.objects.db_index)
            filt = subindex.objects.filter_kwargs_for_value
        else:
            index = self._lookup_index(field)
            func = index.objects.db_index
            filt = index.objects.filter_kwargs_for_value
        self.indexes[collection][field.name] = {'map':func, 'filter':filt}
    
    def _lookup_index(self, field):
        for key, val in self.INDEXES:
            if isinstance(field, key):
                return val
    
    def update_indexes(self, document, collection, data):
        document.clear_indexes()
        for field_name, entry in self.indexes.get(collection, dict()).iteritems():
            if field_name in data:
                index_func = entry['map']
                index_func(document, field_name, data[field_name])
        

