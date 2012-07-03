from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin, SchemaAdmin

from common import SimpleDocument, SimpleSchema

class MockView:
    def __init__(self, request):
        self.request = request
    
    def dotpath(self):
        return None
    
    def next_dotpath(self):
        return None

class AdminFormFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.admin_model = DocumentAdmin(SimpleDocument, admin.site, schema=SimpleDocument)
        self.schema_model = SchemaAdmin(SimpleDocument, admin.site, schema=SimpleSchema, documentadmin=self.admin_model)
        self.factory = RequestFactory()
        User.objects.all().delete() #why?
        self.super_user = User.objects.create(is_staff=True, is_active=True, is_superuser=True, username='admin_testuser')
    
    def test_formfield_for_field_with_complex_list_field(self):
        request = self.factory.get('/')
        prop = SimpleDocument._meta.fields['complex_list']
        field = prop.get_form_field_class()
        kwargs = prop.formfield_kwargs()
        kwargs['request'] = request
        
        view = MockView(request)
        admin_field = self.admin_model.formfield_for_field(prop, field, view, **kwargs)
        field_html = admin_field.widget.render('complex_list', [])
        self.assertTrue('value="add"' in field_html)
    
    def test_inline_form_field_for_field_with_complex_list_field(self):
        request = self.factory.get('/')
        instances = self.admin_model.get_default_inline_instances()
        self.assertEqual(len(instances), 1)
        
        inline_admin = instances[0]
        prop = inline_admin.schema._meta.fields['gallery']
        field = prop.get_form_field_class()
        kwargs = prop.formfield_kwargs()
        kwargs['request'] = request
        view = MockView(request)
        admin_field = inline_admin.formfield_for_field(prop, field, view, **kwargs)
        field_html = admin_field.widget.render('complex_list', [])
        self.assertTrue('value="add"' in field_html)
        
    def test_inline_get_formset(self):
        request = self.factory.get('/')
        instances = self.admin_model.get_default_inline_instances()
        self.assertEqual(len(instances), 1)
        view = MockView(request)
        
        inline_admin = instances[0]
        formset = inline_admin.get_formset(request, view=view)
        html = list()
        for form in formset(instance=SimpleDocument()):
            assert form._meta.formfield_callback
            html.append(form.as_table())
        html = '\n'.join(html)
        self.assertTrue('value="add"' in html)

