from dockit.core.serializers.python import Serializer, Deserializer
from django.utils import unittest

from common import ParentDocument, ChildDocument

class PythonSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.serializer = Serializer()
        #self.deserializer = Deserializer()
    
    def test_serialize(self):
        child = ChildDocument(charfield='bar')
        parent = ParentDocument(title='foo', subdocument=child)
        data = parent.to_portable_primitive(parent)
        result = self.serializer.serialize([child, parent])
        self.assertEqual(len(result), 2)
        entry = result[1]
        self.assertTrue('fields' in entry)
        self.assertEqual(len(entry['fields']), 2)
        self.assertEqual(entry['fields'], data)
    
    def test_deserialize(self):
        payload = [{'natural_key': {'charfield': 'bar'}, 'pk': u'None', 'model': u'serializers.childdocument', 'fields': {'charfield': u'bar'}}, 
                   {'natural_key': {'pk': 'None'}, 'pk': u'None', 'model': u'serializers.parentdocument', 'fields': {'subdocument': {'charfield': 'bar'}, 'title': u'foo'}}]
        objects = list(Deserializer(payload))
        self.assertEqual(len(objects), 2)
        obj = objects[1]
        #assert False, str(obj.object.to_primitive(obj.object))
        self.assertEqual(obj.object['title'], 'foo')
        
        saved_objects = list()
        for obj in objects:
            saved_objects.append(obj.save())
        
        for obj in saved_objects:
            obj.normalize_portable_primitives()
            obj.save()

