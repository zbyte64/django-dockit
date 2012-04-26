from django.utils import simplejson

from dockit.backends.generic.backend import BaseKeyValueBackend, BaseMapReduceBackend
from dockit.backends.queryset import BaseDocumentQuery

from models import DocumentStore, RegisteredIndex

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

class DjangoModelKeyValueBackend(BaseKeyValueBackend):
    def save(self, collection, doc_id, data, encoded_data):
        document = DocumentStore(collection=collection, data=encoded_data)
        if doc_id is not None:
            document.pk = doc_id
        #CONSIDER this does not look before we save
        document.save()
        data[self.get_id_field_name()] = document.pk
    
    def get(self, collection, doc_id):
        try:
            document = DocumentStore.objects.get(collection=collection, pk=doc_id)
        except DocumentStore.DoesNotExist:
            raise KeyError
        data = simplejson.loads(document.data)
        data[self.get_id_field_name()] = document.pk
        return data
    
    def delete(self, collection, doc_id):
        return DocumentStore.objects.filter(collection=collection, pk=doc_id).delete()


class DjangoModelMapReduceBackend(BaseMapReduceBackend):
    
    def on_save(self, collection, doc_id, data, encoded_data):
        RegisteredIndex.objects.on_save(collection, doc_id, data, encoded_data)
    
    def on_delete(self, collection, doc_id):
        RegisteredIndex.objects.on_delete(collection, doc_id)
    
    def remove_index(self, query_index):
        RegisteredIndex.objects.remove_index(query_index)
    
    def get_query(self, query_index):
        raise NotImplementedError
    
    def register_index(self, query_index):
        RegisteredIndex.objects.register_index(query_index) #get & update or create
    '''
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
    '''


