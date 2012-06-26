from common import DataAdaptor, register_adaptor

from django.utils import simplejson

class JSONAdaptor(DataAdaptor):
    def deserialize(self, file_obj):
        return simplejson.loads(file_obj)

register_adaptor('json', JSONAdaptor)

class XMLAdaptor(DataAdaptor):
    pass

register_adaptor('xml', XMLAdaptor)
