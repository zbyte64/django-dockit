from backends import get_document_backend

class SchemaBase(type):
    """
    Metaclass for all schemas.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(SchemaBase, cls).__new__
        
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        new_class._fields = dict()
        
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)
        return new_class
    
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

class Schema(object):
    __metaclass__ = SchemaBase
    
    def __init__(self, **kwargs):
        #super(Schema, self).__init-_()
        self._data = dict()
        for key, value in kwargs.iteritems():
            #TODO check that key is a field or _data
            setattr(self, key, value)
    
    @classmethod
    def to_primitive(cls, val):
        #CONSIDER shouldn't val be a schema?
        if hasattr(val, '_data'):
            return val._data
        return val
    
    @classmethod
    def to_python(cls, val):
        return cls(_data=val)
    
    def __getattr__(self, name):
        try:
            return super(Schema, self).__getattr__(name)
        except AttributeError:
            if name in self._fields:
                return self._fields[name].to_python(self._data.get(name))
            raise
    
    def __setattr__(self, name, val):
        if name in self._fields:
            field = self._fields[name]
            store_val = field.to_primitive(val)
            self._data[name] = store_val
        else:
            super(Schema, self).__setattr__(name, val)

class Document(Schema):
    collection = None
    
    def get_id(self):
        backend = get_document_backend()
        return backend.get_id(self._data)
    
    def save(self):
        backend = get_document_backend()
        backend.store(self.collection, self._data)
    
    @classmethod
    def load(cls, doc_id):
        backend = get_document_backend()
        data = backend.fetch(cls.collection, doc_id)
        return cls.to_python(data)

