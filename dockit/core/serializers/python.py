"""
A Python "serializer". Doesn't do much serializing per se -- just converts to
and from basic Python data types (lists, dicts, strings, etc.). Useful as a basis for
other serializers.
"""

from django.utils.encoding import smart_unicode

from dockit.core.serializers import base
from dockit.schema.loading import get_base_document

class Serializer(base.Serializer):
    """
    Serializes a QuerySet to basic Python objects.
    """

    internal_use_only = True

    def start_serialization(self):
        self._current = None
        self.objects = []

    def end_serialization(self):
        pass

    def start_object(self, obj):
        self._current = obj.to_portable_primitive(obj)
        pk_field = obj._meta.get_id_field_name()
        if pk_field in self._current:
            del self._current[pk_field]
        self._current.pop('@natural_key', None)
        self._current.pop('@natural_key_hash', None)

    def end_object(self, obj):
        entry = {
            "collection"  : smart_unicode(obj._meta.collection),
            "pk"     : smart_unicode(obj._get_pk_val(), strings_only=True),
            "natural_key": obj.natural_key,
            "natural_key_hash": obj.natural_key_hash,
            "fields" : self._current,
        }
        self.objects.append(entry)
        self._current = None

    def getvalue(self):
        return self.objects

def Deserializer(object_list, **options):
    """
    Deserialize simple Python objects back into Django ORM instances.

    It's expected that you pass the Python objects themselves (instead of a
    stream or a string) to the constructor
    """
    #models.get_apps()
    use_natural_keys = options.get('use_natural_keys', True)
    for d in object_list:
        # Look up the model and starting build a dict of data for it.
        doc_cls = get_base_document(d["collection"])
        data = d['fields']
        if use_natural_keys:
            data['@natural_key'] = d['natural_key']
        else:
            data[doc_cls._meta.pk.attname] = doc_cls._meta.pk.to_python(d["pk"])
        
        yield base.DeserializedObject(doc_cls.to_python(data), natural_key=d['natural_key'])

