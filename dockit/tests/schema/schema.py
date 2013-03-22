from django.utils import unittest
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from common import SimpleSchema, SimpleDocument, ValidatingDocument, SimpleSchema2


class SchemaTestCase(unittest.TestCase):
    def test_to_primitive(self):
        obj = SimpleSchema(_python_data={'charfield':'charmander'})
        prim_data = obj.to_primitive(obj)
        self.assertEqual(prim_data, {'charfield':'charmander'})
    
    def test_to_portable_primitive(self):
        obj = SimpleSchema(_python_data={'charfield':'charmander'})
        prim_data = obj.to_portable_primitive(obj)
        self.assertEqual(prim_data, {'charfield':'charmander'})
    
    def test_to_python(self):
        obj = SimpleSchema(_primitive_data={'charfield':'charmander'})
        py_obj = obj.to_python({'charfield':'charmander'})
        self.assertEqual(obj._primitive_data, py_obj._primitive_data)
    
    def test_from_portable_primitive(self):
        obj = SimpleSchema(_primitive_data={'charfield':'charmander'})
        assert obj.charfield, 'Failed to initialize python data'
        py_obj = obj.to_python({'charfield':'charmander'})
        py_obj.normalize_portable_primitives()
        self.assertEqual(obj._primitive_data, py_obj._primitive_data)
    
    def test_traverse(self):
        obj = SimpleSchema(charfield='charmander')
        self.assertEqual(obj.dot_notation('charfield'), 'charmander')
    
    def test_natural_key_creation(self):
        obj = SimpleDocument()
        obj.save()
        self.assertTrue('@natural_key' in obj._primitive_data)
        self.assertTrue('@natural_key_hash' in obj._primitive_data)
        

class DocumentValidationTestChase(unittest.TestCase):
    def test_validation(self):
        obj = ValidatingDocument()
        try:
            obj.full_clean()
        except ValidationError as error:
            self.assertFalse('allow_null' in error.message_dict)
        else:
            self.fail('Validation is broken')
        
        obj.with_choices = 'c'
        obj.not_null = 'foo'
        obj.allow_blank = ''
        obj.not_blank = ''
        try:
            obj.subschema = 'Not a schema'
        except ValidationError as error:
            pass
        else:
            self.fail('Setting a subschema should evaluate immediately')
        
        try:
            obj.full_clean()
        except ValidationError as error:
            self.assertFalse('not_null' in error.message_dict, str(error))
            self.assertFalse('allow_blank' in error.message_dict, str(error))
            self.assertTrue('with_choices' in error.message_dict, str(error))
            self.assertTrue('not_blank' in error.message_dict, str(error))
            self.assertTrue('subschema' in error.message_dict, str(error))
        else:
            self.fail('Validation is broken')
        
        try:
            obj.subschema = SimpleSchema2()
        except ValidationError as error:
            pass
        else:
            self.fail('Setting a subschema should evaluate immediately')
        
        obj.with_choices = 'b'
        obj.not_blank = 'foo'
        obj.subschema = SimpleSchema()
        obj.full_clean()

