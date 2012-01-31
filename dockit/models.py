import dockit
from dockit.backends import get_document_backend

from copy import deepcopy

class TemporaryDocument(dockit.Document):
    pass

class FactoryMeta(object):
    def __init__(self, attributes):
        for key, value in attributes.iteritems():
            setattr(self, key, value)

def create_temporary_document_class(document_cls):
    
    class TempDocument(document_cls):
        class Meta:
            virtual = True
            collection = TemporaryDocument._meta.collection
        
        def commit_changes(self, instance=None):
            if instance is None:
                instance = document_cls()
            
            data = self.to_primitive(self)
            
            #remove id field
            backend = get_document_backend()
            data.pop(backend.get_id_field_name(), None)
            if instance and instance.pk:
                data[backend.get_id_field_name()] = instance.pk
            
            instance._primitive_data = data
            instance.save()
            return instance
        
        def copy_from_instance(self, instance):
            backend = get_document_backend()
            data = instance.to_primitive(instance)
            data.pop(backend.get_id_field_name())
            
            backend = get_document_backend()
            data.pop(backend.get_id_field_name(), None)
            self._primitive_data = data
            self._python_data = dict()
        
        def save(self, *args, **kwargs):
            return dockit.Document.save(self, *args, **kwargs)
        
        def delete(self, *args, **kwargs):
            return dockit.Document.delete(self, *args, **kwargs)
    
    #TODO investigate: Exception RuntimeError: 'maximum recursion depth exceeded in __subclasscheck__' in <type 'exceptions.AttributeError'> ignored
    TempDocument._meta.fields = deepcopy(document_cls._meta.fields)
    for name, value in TempDocument._meta.fields.iteritems():
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(TempDocument, name)
        else:
            setattr(TempDocument, name, value)
    
    return TempDocument
