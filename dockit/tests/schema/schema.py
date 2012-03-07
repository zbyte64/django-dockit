from dockit import schema
from dockit.schema.schema import create_document, create_schema

from django.utils import unittest

class SimpleSchema(schema.Schema): #TODO make a more complex testcase
    charfield = schema.CharField()

class SchemaTestCase(unittest.TestCase):
    def test_to_primitive(self):
        obj = SimpleSchema(_python_data={'charfield':'charmander'})
        prim_data = obj.to_primitive(obj)
        self.assertEqual(prim_data, {'charfield':'charmander'})
    
    def test_to_python(self):
        obj = SimpleSchema(_primitive_data={'charfield':'charmander'})
        py_data = obj.to_python(obj)
        self.assertEqual(py_data, {'charfield':'charmander'})
    
    def test_traverse(self):
        obj = ScimpleSchema(charfield='charmander')
        self.assertEqual(obj.dot_notation('charfield'), 'charmander')
        
