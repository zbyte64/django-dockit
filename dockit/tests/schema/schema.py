from dockit.schema.schema import create_document, create_schema

from django.utils import unittest

from common import SimpleSchema

class SchemaTestCase(unittest.TestCase):
    def test_to_primitive(self):
        obj = SimpleSchema(_python_data={'charfield':'charmander'})
        prim_data = obj.to_primitive(obj)
        self.assertEqual(prim_data, {'charfield':'charmander'})
    
    def test_to_python(self):
        obj = SimpleSchema(_primitive_data={'charfield':'charmander'})
        py_obj = obj.to_python({'charfield':'charmander'})
        self.assertEqual(obj._primitive_data, py_obj._primitive_data)
    
    def test_traverse(self):
        obj = SimpleSchema(charfield='charmander')
        self.assertEqual(obj.dot_notation('charfield'), 'charmander')

