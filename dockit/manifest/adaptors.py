from common import DataAdaptor, register_adaptor

from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

class JSONAdaptor(DataAdaptor):
    def deserialize(self, file_obj):
        return simplejson.loads(file_obj)
    
    def serialize(self, python_objects):
        return simplejson.dumps(python_objects, cls=DjangoJSONEncoder)

register_adaptor('json', JSONAdaptor)

class XMLAdaptor(DataAdaptor):
    pass

register_adaptor('xml', XMLAdaptor)
