from dockit.schema import fields

from django.utils import unittest

import datetime
from decimal import Decimal

class BaseFieldTestCase(unittest.TestCase):
    EXAMPLE_VALUES = []
    EXAMPLE_PRIMITIVE_VALUES = []
    field_class = fields.BaseField
    
    def get_field_kwargs(self):
        return {}
    
    def get_field(self, **kwargs):
        params = self.get_field_kwargs()
        params.update(kwargs)
        return self.field_class(**params)
    
    def test_handles_null_value(self):
        field = self.get_field(null=True)
        val = field.to_python(None)
        self.assertEqual(val, None)
    
    def test_to_python_to_primitive(self):
        field = self.get_field()
        
        for val in self.EXAMPLE_VALUES:
            primitive = field.to_primitive(val)
            py_val = field.to_python(primitive)
            self.assertEqual(py_val, val)
        
        for val in self.EXAMPLE_PRIMITIVE_VALUES:
            py_val = field.to_pyhon(val)
            primitive = field.to_primitive(py_val)
            self.assertEqual(val, primitive)
        
    def test_form_field(self):
        field = self.get_field()
        field.formfield()
    
    def test_get_choices(self):
        field = self.get_field()
        field.get_choices()
    
    def test_json_serializable(self):
        field = self.get_field()
        for val in self.EXAMPLE_VALUES:
            primitive = field.to_primitive(val)
            #TODO attempt to serialize
    
    def test_traverse_dotpath(self):
        pass #TODO raise skipped test

class CharFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ["abc", u"def"] #TODO good unicode values
    field_class = fields.CharField

class IntegerFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [1, 3243455]
    field_class = fields.IntegerField

class BigIntegerFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [1, 3243455, 2**32+1]
    field_class = fields.BigIntegerField

class BooleanFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [True, False]
    field_class = fields.BooleanField

class DateFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [datetime.date(2001,1,1)]
    field_class = fields.DateField

class DateTimeFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [datetime.datetime(2001,1,1)]
    field_class = fields.DateTimeField

class DecimalFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = [1, 2, Decimal('1.5')]
    field_class = fields.DecimalField

class EmailFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ['z@z.com']
    field_class = fields.EmailField

class IPAddressFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ['127.0.0.1']
    field_class = fields.IPAddressField

class SlugFieldTestCase(BaseFieldTestCase):
    EXAMPLE_VALUES = ['slug']
    field_class = fields.SlugField

class TimeFieldTestCase(BaseFieldTestCase):
    field_class = fields.TimeField

#TODO complex field types

