from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin
from dockit.admin.views import DocumentProxyView, DeleteView, IndexView, HistoryView

from common import SimpleDocument

class AdminViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.admin_model = DocumentAdmin(SimpleDocument, admin.site)
        self.factory = RequestFactory()
        User.objects.all().delete() #why?
        self.super_user = User.objects.create(is_staff=True, is_active=True, is_superuser=True, username='admin_testuser')
    
    def test_changelist_view(self):
        kwargs = self.admin_model.get_view_kwargs()
        view = IndexView.as_view(**kwargs)
        request = self.factory.get('/')
        request.user = self.super_user
        response = view(request)
    
    def test_create_view(self):
        kwargs = self.admin_model.get_view_kwargs()
        view = DocumentProxyView.as_view(**kwargs)
        request = self.factory.get('/add/')
        request.user = self.super_user
        response = view(request)

