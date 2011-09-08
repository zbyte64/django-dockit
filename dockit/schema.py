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
        self._primitive_data = dict()
        self._python_data = dict()
        for key, value in kwargs.iteritems():
            #TODO check that key is a field or _data
            setattr(self, key, value)
    
    @classmethod
    def to_primitive(cls, val):
        #CONSIDER shouldn't val be a schema?
        if hasattr(val, '_primitive_data') and hasattr(val, '_python_data'):
            #we've cached python values on access, we need to pump these back to the primitive dictionary
            for name, entry in val._python_data.iteritems():
                val._primitive_data[name] = val._fields[name].to_primitive(entry)
            return val._primitive_data
        assert False
        return val
    
    @classmethod
    def to_python(cls, val):
        return cls(_primitive_data=val)
    
    def __getattribute__(self, name):
        fields = object.__getattribute__(self, '_fields')
        if name in fields:
            python_data = object.__getattribute__(self, '_python_data')
            if name not in python_data:
                primitive_data = object.__getattribute__(self, '_primitive_data')
                python_data[name] = fields[name].to_python(primitive_data.get(name))
            return python_data[name]
        return object.__getattribute__(self, name)
    
    def __setattr__(self, name, val):
        if name in self._fields:
            self._python_data[name] = val
            #field = self._fields[name]
            #store_val = field.to_primitive(val)
            #self._primtive_data[name] = store_val
        else:
            super(Schema, self).__setattr__(name, val)

class Document(Schema):
    collection = None
    
    def get_id(self):
        backend = get_document_backend()
        return backend.get_id(self._primitive_data)
    
    def save(self):
        backend = get_document_backend()
        backend.store(self.collection, type(self).to_primitive(self))
    
    @classmethod
    def load(cls, doc_id):
        backend = get_document_backend()
        data = backend.fetch(cls.collection, doc_id)
        return cls.to_python(data)
    
    @classmethod
    def root_index(cls):
        backend = get_document_backend()
        return backend.root_index(cls, cls.collection)

