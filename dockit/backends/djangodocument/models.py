from django.db import models

import datetime
from decimal import Decimal

from managers import BaseIndexManager, DocumentManager

class DocumentStore(models.Model):
    collection = models.CharField(max_length=128)
    data = models.TextField()
    
    objects = DocumentManager()
    
    def clear_indexes(self):
        for index in type(self).objects.index_models.itervalues():
            index['model'].objects.clear_db_index(self)

class BaseIndex(models.Model):
    document = models.ForeignKey(DocumentStore)
    index = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    objects = BaseIndexManager()
    
    class Meta:
        abstract = True

class IntegerIndex(BaseIndex):
    value = models.IntegerField(null=True)
DocumentStore.objects.register_index_model('int', IntegerIndex, int)

class BooleanIndex(BaseIndex):
    value = models.BooleanField()
DocumentStore.objects.register_index_model('bool', BooleanIndex, bool)

class StringIndex(BaseIndex):
    value = models.CharField(max_length=512)
DocumentStore.objects.register_index_model('char', StringIndex, basestring)

class TextIndex(BaseIndex):
    value = models.TextField()
DocumentStore.objects.register_index_model('text', TextIndex, basestring)

class DateTimeIndex(BaseIndex):
    value = models.DateTimeField(null=True)
DocumentStore.objects.register_index_model('datetime', DateTimeIndex, datetime.datetime)

class DateIndex(BaseIndex):
    value = models.DateField(null=True)
DocumentStore.objects.register_index_model('date', DateIndex, datetime.date)

class FloatIndex(BaseIndex):
    value = models.FloatField(null=True)
DocumentStore.objects.register_index_model('float', FloatIndex, float)

class TimeIndex(BaseIndex):
    value = models.TimeField(null=True)
DocumentStore.objects.register_index_model('time', TimeIndex, datetime.time)

class DecimalIndex(BaseIndex):
    value = models.DecimalField(max_digits=19, decimal_places=10, null=True)
DocumentStore.objects.register_index_model('decimal', DecimalIndex, Decimal)

