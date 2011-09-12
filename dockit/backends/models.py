from django.db import models
from django.utils import simplejson

from base import BaseDocumentStorage

class DocumentStore(models.Model):
    collection = models.CharField(max_length=128)
    data = models.TextField()

class BaseIndex(models.Model):
    key = models.CharField(max_length=255)
    collection = models.CharField(max_length=128, db_index=True)
    document = models.ForeignKey(DocumentStore)
    value = None #you are to define this
    
    class Meta:
        abstract = True

class CharIndex(BaseIndex):
    value = models.CharField(max_length=255, db_index=True)

class IntegerIndex(BaseIndex):
    value = models.IntegerField()

class ModelDocumentStorage(object):
    def store(self, collection, data):
        doc_id = self.get_id(data)
        document = DocumentStore(collection=collection, data=simplejson.dumps(data))
        if doc_id is not None:
            document.pk = doc_id
        #CONSIDER this does not look before we save
        document.save()
        data['_pk'] = document.pk
    
    def fetch(self, collection, doc_id):
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
    
    def root_index(self, doc_class, collection):
        qs = DocumentStore.objects.filter(collection=collection)
        
        def entry_to_document(entry):
            data = simplejson.loads(entry.data)
            data['_pk'] = entry.pk
            return doc_class.to_python(data)
        
        def result_set():
            for entry in qs:
                yield entry_to_document(entry)
        
        return list(result_set())

