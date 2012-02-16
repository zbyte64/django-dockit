from django.db.models import Model, Q

from dockit.backends.indexer import BaseIndexer
from dockit.schema import fields#, Document

from models import DocumentStore, StringIndex
import models as indexes
from backend import ModelDocumentStorage, DocumentQuery

#TODO need a mechanism for back populating indexes, must be task based

class Indexer(object):
    def __init__(self, doc_class, index_creator, dotpath, name):
        self.doc_class = doc_class
        self.index_creator = index_creator
        self.dotpath = dotpath
        self.name = name
    
    def __call__(self, document):
        if self.dotpath in ('pk', '_pk'):
            return
        try:
            value = document.dot_notation(self.dotpath)
        except (KeyError, IndexError):
            return
        
        if value is None:
            return #TODO proper handling
        if isinstance(value, list):
            for val in value:
                self.index_creator(document.pk, self.name, val)
        else:
            self.index_creator(document.pk, self.name, value)

class ExactIndexer(BaseIndexer):
    INDEXES = [(fields.TextField, indexes.StringIndex),
           (fields.CharField, indexes.StringIndex),
           (fields.IntegerField, indexes.IntegerIndex),
           (fields.FloatField, indexes.FloatIndex),
           (fields.DecimalField, indexes.DecimalIndex),
           (fields.BooleanField, indexes.BooleanIndex),
           (fields.DateField, indexes.DateIndex),
           (fields.DateTimeField, indexes.DateTimeIndex),
           (fields.TimeField, indexes.TimeIndex),
           (Model, indexes.StringIndex),
           (fields.ReferenceField, indexes.StringIndex),
           (fields.ModelReferenceField, indexes.StringIndex),]
    
    def __init__(self, document, filter_operation):
        self.document = document
        self.filter_operation = filter_operation
        self.dotpath = self.filter_operation.dotpath()
        self.generate_index()
    
    def generate_index(self):
        collection = self.document._meta.collection
        field = self.document._meta.dot_notation_to_field(self.dotpath)
        
        subindex = self._lookup_index(field)
        if subindex is None and hasattr(field, 'subfield'):
            subindex = self._lookup_index(field.subfield)
        
        if subindex is None:
            subindex = StringIndex
            #raise TypeError("Could not identify an apropriate index for: %s" % field)
        
        func = Indexer(self.document, subindex.objects.db_index, self.dotpath, self.filter_operation.key)
        filt = subindex.objects.filter_kwargs_for_operation
        unique_values = subindex.objects.unique_values
        clear = subindex.objects.clear_db_index
        
        self.index_functions = {'map':func, 'filter':filt, 'unique_values':unique_values, 'clear':clear}
    
    def _lookup_index(self, field):
        for key, val in self.INDEXES:
            if isinstance(field, key):
                return val
    
    def on_document_save(self, instance):
        self.index_functions['map'](instance)
    
    def on_document_delete(self, instance):
        self.index_functions['clear'](instance.pk)
        
    def filter(self):
        return Q(**self.index_functions['filter'](self.filter_operation))
    
    def values(self):
        return self.index_functions['unique_values'](self.filter_operation.key)

ModelDocumentStorage.register_indexer(ExactIndexer, 'exact', 'iexact', 'startswith', 'endswith', 'year', 'month', 'day')

