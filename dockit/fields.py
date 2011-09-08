
class BaseField(object):
    def contribute_to_class(self, cls, name):
        self.name = name
        cls._fields[name] = self
        setattr(cls, name, self)
    
    def to_primitive(self, val):
        """
        Takes a python object and returns an object that is [json] serializable
        """
        return val
    
    def to_python(self, val):
        return val

class BaseTypedField(BaseField):
    coerce_function = None
    
    def to_primitive(self, val):
        return self.coerce_function(val)

class TextField(BaseTypedField):
    coerce_function = unicode

class IntegerField(BaseTypedField):
    coerce_function = int

class ObjectField(BaseField):
    def __init__(self, schema):
        self.schema = schema
    
    def to_primitive(self, val):
        return self.schema.to_primitive(val)
    
    def to_python(self, val):
        return self.schema.to_python(val)

class ListField(BaseField):
    def __init__(self, schema):
        self.schema = schema
    
    def to_primitive(self, val):
        ret = list()
        if val is None:
            return ret
        for item in val:
            ret.append(self.schema.to_primitive(item))
        return ret
    
    def to_python(self, val):
        ret = list()
        if val is None:
            return ret
        for item in val:
            ret.append(self.schema.to_python(item))
        return ret

class ReferenceField(BaseField):
    def __init__(self, document):
        assert hasattr(document, 'load')
        assert hasattr(document, 'get_id')
        self.document = document
    
    def to_primitive(self, val):
        return val.get_id()
    
    def to_python(self, val):
        return self.document.load(val)

class ModelReferenceField(BaseField):
    def __init__(self, model):
        self.model = model
    
    def to_primitive(self, val):
        return val.pk
    
    def to_python(self, val):
        return self.model.objects.get(pk=val)

