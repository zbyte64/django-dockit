from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

from dockit.backends.base import BaseDocumentStorage, BaseIndexStorage
from dockit.backends.queryset import BaseDocumentQuery
from dockit.backends import get_index_router

from models import DocumentStore, RegisteredIndex, RegisteredIndexDocument

class DocumentQuery(BaseDocumentQuery):
    def __init__(self, query_index, queryset):
        super(DocumentQuery, self).__init__(query_index)
        self.queryset = queryset
    
    def wrap(self, entry):
        data = simplejson.loads(entry.data)
        data['_pk'] = entry.pk
        return self.document.to_python(data)
    
    def delete(self):
        return self.queryset.delete()
    
    def get_from_filter_operations(self, filter_operations):
        queryset = self.queryset
        for op in filter_operations:
            indexer = self._get_indexer_for_operation(self.document, op)
            queryset = queryset.filter(indexer.filter())
        try:
            return self.wrap(queryset.get())
        except self.queryset.model.DoesNotExist:
            raise self.document.DoesNotExist
    
    def values(self):
        queryset = self.queryset
        for op in query_index.indexes:
            indexer = self._get_indexer_for_operation(self.document, op)
        raise NotImplementedError
    
    def __len__(self):
        return self.queryset.count()
    
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

class ModelIndexStorage(BaseIndexStorage):
    name = "djangomodel"
    _indexers = dict() #TODO this should be automatic
    
    def __init__(self):
        self.indexes = dict()
        import indexers
    
    def _index_document(self, instance):
        indexes = self.indexes.get(instance._meta.collection, set())
        for index in indexes:
            indexer = self._get_indexer_for_operation(type(instance), index)
            indexer.on_document_save(instance)
    
    def register_index(self, query_index):
        RegisteredIndex.objects.register_index(query_index)
    
    def get_query(self, query_index):
        #lookup the appropriate query index
        match = get_index_router().get_effective_queryset(query_index)
        query_index = match['queryset']
        document = query_index.document
        queryset = RegisteredIndexDocument.objects.filter(index__collection=document._meta.collection, index__query_hash=query_index._index_hash())
        for op in match['inclusions']:
            indexer = self._get_indexer_for_operation(document, op)
            queryset = queryset.filter(indexer.filter())
        for op in match['exclusions']:
            indexer = self._get_indexer_for_operation(document, op)
            queryset = queryset.exclude(indexer.filter())
        return DocumentQuery(query_index, queryset)
    
    def on_save(self, doc_class, collection, doc_id, data):
        RegisteredIndex.objects.on_save(collection, doc_id, data)
    
    def on_delete(self, doc_class, collection, doc_id):
        RegisteredIndex.objects.on_delete(collection, doc_id)

class ModelDocumentStorage(BaseDocumentStorage):
    name = "djangomodel"
    
    def get_id_field_name(self):
        return '_pk'
    
    def save(self, doc_class, collection, data):
        doc_id = self.get_id(data)
        encoded_data = simplejson.dumps(data, cls=DjangoJSONEncoder)
        document = DocumentStore(collection=collection, data=encoded_data)
        if doc_id is not None:
            document.pk = doc_id
        #CONSIDER this does not look before we save
        document.save()
        data[self.get_id_field_name()] = document.pk
    
    def get(self, doc_class, collection, doc_id):
        try:
            document = DocumentStore.objects.get(collection=collection, pk=doc_id)
        except DocumentStore.DoesNotExist:
            raise doc_class.DoesNotExist
        data = simplejson.loads(document.data)
        data[self.get_id_field_name()] = document.pk
        return data
    
    def delete(self, doc_class, collection, doc_id):
        return DocumentStore.objects.filter(collection=collection, pk=doc_id).delete()
    
    def get_query(self, query_index):
        document = query_index.document
        queryset = DocumentStore.objects.filter(collection=query_index.document._meta.collection)
        return DocumentQuery(query_index, queryset)

