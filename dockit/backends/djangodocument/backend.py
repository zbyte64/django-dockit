from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

from dockit.backends.base import BaseDocumentStorage, BaseDocumentQuerySet

from models import DocumentStore

class DocumentQuery(BaseDocumentQuerySet):
    def __init__(self, queryset, doc_class):
        self.queryset = queryset
        self.doc_class = doc_class
        super(DocumentQuery, self).__init__()
    
    def wrap(self, entry):
        data = simplejson.loads(entry.data)
        data['_pk'] = entry.pk
        return self.doc_class.to_python(data)
    
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
    
    def _check_for_operation(self, other):
        if not isinstance(other, DocumentQuery):
            raise TypeError, "operation may only be done against other Document Queries"
        if self.doc_class != other.doc_class:
            raise TypeError, "operation may only be done with the same document type"
    
    def __and__(self, other):
        self._check_for_operation(other)
        cls = type(self)
        queryset = self.queryset & other.queryset
        return cls(queryset, self.doc_class)
    
    def __or__(self, other):
        self._check_for_operation(other)
        cls = type(self)
        queryset = self.queryset | other.queryset
        return cls(queryset, self.doc_class)

class ModelDocumentStorage(BaseDocumentStorage):
    name = "djangomodel"
    
    def __init__(self):
        self.indexes = dict()
    
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
    
    def all(self, doc_class, collection):
        qs = DocumentStore.objects.filter(collection=collection)
        return DocumentQuery(qs, doc_class)

