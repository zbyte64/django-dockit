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
    #TODO refactor to something that simply copies the fields and handles dynamic typing
    class TempDocument(document_cls):
        class Meta:
            virtual = True
            proxy = True
            collection = TemporaryDocument._meta.collection
        
        def __init__(self, *args, **kwargs):
            dockit.Document.__init__(self, *args, **kwargs)
        
        def commit_changes(self, doc_id=None):
            backend = get_document_backend()
            id_field = backend.get_id_field_name()
            
            data = self.to_primitive(self)
            data[id_field] = doc_id
            if hasattr(self, '_original_id'):
                data[id_field] = self._original_id
            
            instance = document_cls(_primitive_data=data)
            instance.save()
            return instance
        
        def copy_from_instance(self, instance):
            backend = get_document_backend()
            data = instance.to_primitive(instance)
            self._original_id = data.pop(backend.get_id_field_name(), None)
            self._primitive_data = data
            self._python_data = dict()
        
        @classmethod
        def to_python(cls, val, parent=None):
            if val is None:
                val = dict()
            if cls._meta.typed_field:
                field = cls._meta.fields[cls._meta.typed_field]
                key = val.get(cls._meta.typed_field, None)
                if key:
                    cls = field.schemas[key]
                    cls = create_temporary_document_class(cls)
            return cls(_primitive_data=val, _parent=parent)
        
        def save(self, *args, **kwargs):
            assert self._meta.collection == TemporaryDocument._meta.collection
            return dockit.Document.save(self, *args, **kwargs)
        
        def delete(self, *args, **kwargs):
            assert self._meta.collection == TemporaryDocument._meta.collection
            return dockit.Document.delete(self, *args, **kwargs)
    
    #TODO investigate: Exception RuntimeError: 'maximum recursion depth exceeded in __subclasscheck__' in <type 'exceptions.AttributeError'> ignored
    TempDocument._meta.fields = deepcopy(document_cls._meta.fields)
    for name, value in TempDocument._meta.fields.iteritems():
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(TempDocument, name)
        else:
            setattr(TempDocument, name, value)
    
    return TempDocument
