from dockit.core.serializers.python import Serializer, Deserializer
from django.utils import unittest

class PythonSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.serializer = Serializer()
        #self.deserializer = Deserializer()
    
    def test_serialize(self):
        from dockit.models import TemporaryDocument
        foo = TemporaryDocument(extrafield=1)
        data = foo.to_portable_primitive(foo)
        result = self.serializer.serialize([foo])
        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertTrue('fields' in entry)
        self.assertEqual(len(entry['fields']), 1)
        self.assertEqual(entry['fields'], data)
    
    def test_deserialize(self):
        payload = [{'pk': u'None', 'model': u'dockit.temporarydocument', 'fields': {'extrafield': 1}}]
        objects = list(Deserializer(payload))
        self.assertEqual(len(objects), 1)
        obj = objects[0]
        self.assertEqual(obj.object['extrafield'], 1)

