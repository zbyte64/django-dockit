from django.db import models
from django.utils import simplejson

from base import BaseDocumentStorage

class DocumentStore(models.Model):
    collection = models.CharField(max_length=128)
    data = models.TextField()

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
