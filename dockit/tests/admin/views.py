from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin, SchemaAdmin
from dockit.admin.views import DocumentProxyView, DeleteView, IndexView, HistoryView, ListFieldIndexView

from django.contrib import admin

from common import SimpleDocument, SimpleSchema

from urllib import urlencode

class TestableDeleteView(DeleteView):
    def get_object(self):
        obj = SimpleDocument()
        obj.save()
        return obj

admin.site.register([SimpleDocument], DocumentAdmin)

class AdminViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.admin_model = DocumentAdmin(SimpleDocument, admin.site)
        self.schema_model = SchemaAdmin(SimpleDocument, admin.site, schema=SimpleSchema, documentadmin=self.admin_model)
        self.factory = RequestFactory()
        User.objects.all().delete() #why?
        self.super_user = User.objects.create(is_staff=True, is_active=True, is_superuser=True, username='admin_testuser')
    
    def test_changelist_view(self):
        kwargs = self.admin_model.get_view_kwargs()
        view = IndexView.as_view(**kwargs)
        request = self.factory.get('/')
        request.user = self.super_user
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_create_view(self):
        kwargs = self.admin_model.get_view_kwargs()
        view = DocumentProxyView.as_view(**kwargs)
        request = self.factory.get('/add/')
        request.user = self.super_user
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_list_field_index_view(self):
        kwargs = self.schema_model.get_view_kwargs()
        #kwargs['schema'] = SimpleSchema #TODO why does this break things?
        #assert False, str(dir(ListFieldIndexView))
        view = ListFieldIndexView.as_view(**kwargs)
        view.schema = SimpleSchema
        params = {'_dotpath': 'complex_list'}
        request = self.factory.get('/add/?%s' % urlencode(params))
        request.user = self.super_user
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view(self):
        kwargs = self.admin_model.get_view_kwargs()
        kwargs['object'] = SimpleDocument()
        view = TestableDeleteView.as_view(**kwargs)
        
        request = self.factory.get('/1/delete/')
        request.user = self.super_user
        response = view(request)
        self.assertEqual(response.status_code, 200)
        
        request = self.factory.post('/1/delete/')
        request.user = self.super_user
        response = view(request)
        self.assertEqual(response.status_code, 302)

