from dockit import schema
from dockit.backends import get_document_backend

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from copy import deepcopy

import datetime

class SchemaProxyDict(dict):
    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return TemporaryDocument.generate_document(val)

class TemporaryDocumentInfo(schema.Schema):
    user = schema.ModelReferenceField(User, blank=True, null=True)
    created = schema.DateTimeField(default=datetime.datetime.now)
    
    object_collection = schema.CharField()
    object_id = schema.CharField()
    
    number_of_changes = schema.IntegerField(default=0)

class TemporaryDocument(schema.Document):
    _tempinfo = schema.SchemaField(TemporaryDocumentInfo)
    
    @classmethod
    def generate_document(cls, document):
        class GeneratedTempDocument(cls):
            class Meta:
                proxy = True
        fields = deepcopy(document._meta.fields)
        
        #handle dynamic typing
        if document._meta.typed_field:
            GeneratedTempDocument._meta.typed_field = document._meta.typed_field
            GeneratedTempDocument._meta.typed_key = document._meta.typed_key
            t_field = fields[document._meta.typed_field]
            orignal_schemas = t_field.schemas
            t_field.schemas = SchemaProxyDict(orignal_schemas)
        
        GeneratedTempDocument._meta.fields.update(fields)
        GeneratedTempDocument._meta.original_document = document
        
        for name, value in GeneratedTempDocument._meta.fields.iteritems():
            if hasattr(value, 'contribute_to_class'):
                value.contribute_to_class(GeneratedTempDocument, name)
            else:
                setattr(GeneratedTempDocument, name, value)
        
        return GeneratedTempDocument
    
    def commit_changes(self, doc_id=None):
        document_cls = self._meta.original_document
        
        backend = get_document_backend()
        id_field = backend.get_id_field_name()
        
        data = self.to_primitive(self)
        data[id_field] = doc_id
        data.pop('_tempinfo', None)
        
        instance = document_cls(_primitive_data=data)
        instance.save()
        return instance
    
    @classmethod
    def create_from_instance(cls, instance):
        backend = get_document_backend()
        data = instance.to_primitive(instance)
        instance_id = data.pop(backend.get_id_field_name(), None)
        obj = cls.to_python(data)
        obj._original_id = instance_id
        return obj

def create_temporary_document_class(document_cls):
    return TemporaryDocument.generate_document(document_cls)

#TODO creating an index should optionally populate this table
class ActiveIndex(schema.Document):
    collection = schema.CharField()
    name = schema.CharField() #name assigned in application
    backend = schema.CharField()
    backend_index_identifier = schema.CharField()
    creation_date = schema.DateTimeField(default=datetime.datetime.now)
    #TODO store the index parameters

class DockitPermission(models.Model):
    pass #a content type is required for creating permissions

if 'django.contrib.auth' in settings.INSTALLED_APPS:
    import auth

