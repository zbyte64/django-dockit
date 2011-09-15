from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin
from dockit.admin.views import SchemaFieldView
from dockit.forms import DocumentForm

from models import Book, Publisher, Address

class BookAdmin(DocumentAdmin):
    pass

class AddressFieldView(SchemaFieldView):
    model = Address
    
    uri = 'admin:admin_books_publisher_address'

from django import forms

class PublisherForm(DocumentForm):
    name = forms.CharField()
    address = AddressFieldView.get_field()
    
    class Meta:
        model = Publisher

class PublisherAdmin(DocumentAdmin):
    form_class = PublisherForm #we can't use form, thanks Django Admin
    declared_fieldsets = [(None, {'fields': ['name', 'address']})]
    
    def get_extra_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = patterns('',
            url('address/$', AddressFieldView.as_view(**{'admin':self, 'admin_site':self.admin_site}), name='admin_books_publisher_address')
        )
        return urls

admin.site.register([Book], BookAdmin)
admin.site.register([Publisher], PublisherAdmin)
