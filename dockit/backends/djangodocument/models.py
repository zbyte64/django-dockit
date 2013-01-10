from django.db import models

from dockit.schema.loading import get_base_document

import datetime
from decimal import Decimal

from dockit.backends.djangodocument.managers import BaseIndexManager, DocumentManager, RegisteredIndexManager

class DocumentStore(models.Model):
    collection = models.CharField(max_length=128)
    data = models.TextField()
    
    objects = DocumentManager()
    
    def clear_indexes(self):
        for index in type(self).objects.index_models.itervalues():
            index['model'].objects.clear_db_index(self)

class RegisteredIndex(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    collection = models.CharField(max_length=128, db_index=True)
    query_hash = models.BigIntegerField()
    
    objects = RegisteredIndexManager()
    
    def get_document(self):
        return get_base_document(self.collection)
    
    class Meta:
        unique_together = [('name', 'collection')]

class RegisteredIndexDocument(models.Model):
    index = models.ForeignKey(RegisteredIndex, related_name='documents')
    doc_id = models.CharField(max_length=128, db_index=True)
    data = models.TextField(blank=True) #optionally store a copy of the document for retrieval
    timestamp = models.DateTimeField(auto_now=True)

class BaseIndex(models.Model):
    document = models.ForeignKey(RegisteredIndexDocument)
    param_name = models.CharField(max_length=128, db_index=True)
    
    objects = BaseIndexManager()
    
    class Meta:
        abstract = True

class IntegerIndex(BaseIndex):
    value = models.IntegerField(null=True)
RegisteredIndex.objects.register_index_model('int', IntegerIndex, int)

class LongIndex(BaseIndex):
    value = models.BigIntegerField(null=True)
RegisteredIndex.objects.register_index_model('long', LongIndex, long)

class BooleanIndex(BaseIndex):
    value = models.NullBooleanField()
RegisteredIndex.objects.register_index_model('bool', BooleanIndex, bool)

class StringIndex(BaseIndex):
    value = models.CharField(max_length=512, null=True)
RegisteredIndex.objects.register_index_model('char', StringIndex, (basestring, type(None)))

class TextIndex(BaseIndex):
    value = models.TextField(null=True)
RegisteredIndex.objects.register_index_model('text', TextIndex, basestring)

class DateTimeIndex(BaseIndex):
    value = models.DateTimeField(null=True)
RegisteredIndex.objects.register_index_model('datetime', DateTimeIndex, datetime.datetime)

class DateIndex(BaseIndex):
    value = models.DateField(null=True)
RegisteredIndex.objects.register_index_model('date', DateIndex, datetime.date)

class FloatIndex(BaseIndex):
    value = models.FloatField(null=True)
RegisteredIndex.objects.register_index_model('float', FloatIndex, float)

class TimeIndex(BaseIndex):
    value = models.TimeField(null=True)
RegisteredIndex.objects.register_index_model('time', TimeIndex, datetime.time)

class DecimalIndex(BaseIndex):
    value = models.DecimalField(max_digits=19, decimal_places=10, null=True)
RegisteredIndex.objects.register_index_model('decimal', DecimalIndex, Decimal)

