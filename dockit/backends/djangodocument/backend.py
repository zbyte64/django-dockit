from django.utils import simplejson
from django.db.models import Model

from dockit.backends.base import BaseDocumentStorage
from dockit.schema import fields#, Document

from models import DocumentStore, StringIndex, IntegerIndex

class Indexer(object):
    def __init__(self, doc_class, index_creator, dotpath):
        self.doc_class = doc_class
        self.index_creator = index_creator
        self.dotpath = dotpath
    
    def __call__(self, dbdocument, data):
        document = self.doc_class(_primitive_data=data)
        try:
            value = document.dot_notation(self.dotpath)
        except (KeyError, IndexError):
            return
        
        if isinstance(value, list):
            for val in value:
                self.index_creator(dbdocument, self.dotpath, val)
        else:
            self.index_creator(dbdocument, self.dotpath, value)

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
    
    def get_id_field_name(self):
        return '_pk'
    
    def save(self, collection, data):
        doc_id = self.get_id(data)
        document = DocumentStore(collection=collection, data=simplejson.dumps(data))
        if doc_id is not None:
            document.pk = doc_id
        #CONSIDER this does not look before we save
        document.save()
        data[self.get_id_field_name()] = document.pk
        self.update_indexes(document, collection, data)
    
    def get(self, collection, doc_id):
        try:
            document = DocumentStore.objects.get(collection=collection, pk=doc_id)
        except DocumentStore.DoesNotExist:
            raise #TODO raise proper error
        data = simplejson.loads(document.data)
        data[self.get_id_field_name()] = document.pk
        return data
    
    def delete(self, collection, doc_id):
        return DocumentStore.objects.filter(collection=collection, pk=doc_id).delete()
    
    def define_index(self, collection, index):
        raise NotImplementedError
    
    def all(self, doc_class, collection):
        qs = DocumentStore.objects.filter(collection=collection)
        return DocumentQuery(qs, doc_class)
    
    def filter(self, doc_class, collection, params):
        qs = DocumentStore.objects.filter(collection=collection)
        for key, value in params.iteritems():
            qs = qs.filter(**self.indexes[collection][key]['filter'](key, value))
        return DocumentQuery(qs, doc_class)
    
    def generate_index(self, document, dotpath):
        collection = document._meta.collection
        self.indexes.setdefault(collection, dict())
        field = document.dot_notation_to_field(dotpath)
        
        subindex = self._lookup_index(field)
        if subindex is None and hasattr(field, 'schema'):
            subindex = self._lookup_index(field.schema)
        
        func = Indexer(document, subindex.objects.db_index, dotpath)
        filt = subindex.objects.filter_kwargs_for_value
        
        self.indexes[collection][dotpath] = {'map':func, 'filter':filt}
    
    def _lookup_index(self, field):
        for key, val in self.INDEXES:
            if isinstance(field, key):
                return val
    
    def update_indexes(self, document, collection, data):
        document.clear_indexes()
        for entry in self.indexes.get(collection, dict()).itervalues():
            index_func = entry['map']
            index_func(document, data)


