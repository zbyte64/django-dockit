from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

from dockit.backends.base import BaseDocumentStorage
from dockit.backends.queryset import BaseDocumentQuery

from models import DocumentStore

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

class ModelDocumentStorage(BaseDocumentStorage):
    name = "djangomodel"
    _indexers = dict() #TODO this should be automatic
    
    def __init__(self):
        self.indexes = dict()
        import indexers
    
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
        self._index_document(doc_class.to_python(data))
    
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
    
    def _index_document(self, instance):
        indexes = self.indexes.get(instance._meta.collection, set())
        for index in indexes:
            indexer = self._get_indexer_for_operation(type(instance), index)
            indexer.on_document_save(instance)
    
    def register_index(self, query_index):
        indexes = set(query_index.inclusions + query_index.exclusions + query_index.indexes)
        document = query_index.document
        self.indexes.setdefault(document._meta.collection, set())
        self.indexes[document._meta.collection].update(indexes)
    
    def get_query(self, query_index):
        document = query_index.document
        queryset = DocumentStore.objects.filter(collection=query_index.document._meta.collection)
        for op in query_index.inclusions:
            indexer = self._get_indexer_for_operation(document, op)
            queryset = queryset.filter(indexer.filter())
        for op in query_index.exclusions:
            indexer = self._get_indexer_for_operation(document, op)
            queryset = queryset.exclude(indexer.filter())
        return DocumentQuery(query_index, queryset)

