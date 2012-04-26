from django.db import models

import datetime
from decimal import Decimal

from managers import BaseIndexManager, DocumentManager, RegisteredIndexManager

class DocumentStore(models.Model):
    collection = models.CharField(max_length=128)
    data = models.TextField()
    
    objects = DocumentManager()

class RegisteredIndex(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    collection = models.CharField(max_length=128, db_index=True)
    serialized_query_index = models.TextField()
    
    objects = RegisteredIndexManager()
    
    class Meta:
        unique_together = [('name', 'collection')]

class BaseIndexParam(models.Model):
    doc_id = models.CharField(max_length=128, db_index=True)
    index = models.ForeignKey(RegisteredIndex)
    param_name = models.CharField(max_length=128, db_index=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    objects = BaseIndexManager()
    
    class Meta:
        abstract = True

class IntegerIndexParam(BaseIndexParam):
    value = models.IntegerField(null=True)
DocumentStore.objects.register_index_model('int', IntegerIndexParam, int)

class BooleanIndexParam(BaseIndexParam):
    value = models.BooleanField()
DocumentStore.objects.register_index_model('bool', BooleanIndexParam, bool)

class StringIndexParam(BaseIndexParam):
    value = models.CharField(max_length=512)
DocumentStore.objects.register_index_model('char', StringIndexParam, basestring)

class TextIndexParam(BaseIndexParam):
    value = models.TextField()
DocumentStore.objects.register_index_model('text', TextIndexParam, basestring)

class DateTimeIndexParam(BaseIndexParam):
    value = models.DateTimeField(null=True)
DocumentStore.objects.register_index_model('datetime', DateTimeIndexParam, datetime.datetime)

class DateIndexParam(BaseIndexParam):
    value = models.DateField(null=True)
DocumentStore.objects.register_index_model('date', DateIndexParam, datetime.date)

class FloatIndexParam(BaseIndexParam):
    value = models.FloatField(null=True)
DocumentStore.objects.register_index_model('float', FloatIndexParam, float)

class TimeIndexParam(BaseIndexParam):
    value = models.TimeField(null=True)
DocumentStore.objects.register_index_model('time', TimeIndexParam, datetime.time)

class DecimalIndexParam(BaseIndexParam):
    value = models.DecimalField(max_digits=19, decimal_places=10, null=True)
DocumentStore.objects.register_index_model('decimal', DecimalIndexParam, Decimal)

