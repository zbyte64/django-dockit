from dockit import schema
from dockit.schema.schema import create_document, create_schema
from dockit.forms.forms import document_to_dict, fields_for_document, DocumentForm, documentform_factory

from django.utils import unittest

class SimpleDocument(schema.Document): #TODO make a more complex testcase
    charfield = schema.CharField()

class FormUtilsTestCase(unittest.TestCase):
    def test_document_to_dict(self):
        obj = SimpleDocument(_python_data={'charfield':'charmander'})
        data = document_to_dict(SimpleDocument, obj)
        self.assertTrue('charfield' in data)
        self.assertEqual(data['charfield'], 'charmander')
    
    def test_fields_for_document(self):
        fields = fields_for_document(SimpleDocument)
        self.assertTrue('charfield' in fields)
    
    def test_form_for_schema(self):
        form_cls = documentform_factory(SimpleDocument)

class FormTestCase(unittest.TestCase):
    def setUp(self):
        super(FormTestCase, self).setUp()
        self.form_cls = documentform_factory(SimpleDocument)
    
    def test_blank_init(self):
        form = self.form_cls()
        self.assertFalse(form.is_bound)
    
    def test_data_init(self):
        form = self.form_cls(data={'charfield':'charmander'})
        self.assertTrue(form.is_valid())
    
    def test_instance_init(self):
        obj = SimpleDocument(charfield='charmander')
        form = self.form_cls(instance=obj)
        self.assertFalse(form.is_bound)
    
    def test_instance_update(self):
        obj = SimpleDocument(charfield='charmander')
        form = self.form_cls(instance=obj, data={'charfield':'charmander2'})
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        
        obj2 = form.save()
        self.assertEqual(obj2.charfield, 'charmander2')
    
    def test_instance_create(self):
        form = self.form_cls(data={'charfield':'charmander'})
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.charfield, 'charmander')

