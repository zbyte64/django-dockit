import dockit
from dockit.backends import get_document_backend

class TemporaryDocument(dockit.Document):
    pass

class FactoryMeta(object):
    def __init__(self, attributes):
        for key, value in attributes.iteritems():
            setattr(self, key, value)

def create_temporary_document_class(document_cls):
    original_collection = document_cls._meta.collection
    
    new_meta = dict()
    
    for key in document_cls._meta.DEFAULT_NAMES:
        if hasattr(document_cls._meta, key):
            new_meta[key] = getattr(document_cls._meta, key)
    
    new_meta.update({'virtual':True,
                     'collection': TemporaryDocument._meta.collection,})
    
    class TempDocument(document_cls):
        Meta = FactoryMeta(new_meta)
        
        def commit_changes(self, instance=None):
            if instance is None:
                instance = document_cls()
            
            data = dict(self._primitive_data)
            #remove id field
            backend = get_document_backend()
            data.pop(backend.get_id_field_name(), None)
            
            instance._primitive_data = data
            instance.save()
            return instance
        
        def copy_from_instance(self, instance):
            data = dict(instance._primitive_data)
            
            backend = get_document_backend()
            data.pop(backend.get_id_field_name(), None)
            self._primitive_data = data
    
    assert original_collection == document_cls._meta.collection
    return TempDocument
