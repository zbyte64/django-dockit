from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin
from dockit.admin.views import SchemaFieldView
from dockit.forms import DocumentForm

from models import Book, Publisher, Address, ComplexObject, SubComplexOne, SubComplexTwo

class BookAdmin(DocumentAdmin):
    pass

class AddressFieldView(SchemaFieldView):
    document = Address
    
    uri = 'admin:admin_books_publisher_address'

from django import forms

class PublisherForm(DocumentForm):
    name = forms.CharField()
    address = AddressFieldView.get_field()
    
    class Meta:
        document = Publisher

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

class SubComplexTwoView(SchemaFieldView):
    document = SubComplexTwo
    
    uri = 'admin:admin_books_complex_two'

class SubComplexOneForm(DocumentForm):
    field1 = forms.CharField()
    nested = SubComplexTwoView.get_field()
    
    class Meta:
        document = SubComplexOne

class SubComplexOneView(SchemaFieldView):
    document = SubComplexOne
    form_class = SubComplexOneForm
    
    uri = 'admin:admin_books_complex_one'

class ComplexObjectForm(DocumentForm):
    field1 = forms.CharField()
    nested = SubComplexOneView.get_field()
    
    class Meta:
        document = ComplexObject

class ComplexObjectAdmin(DocumentAdmin):
    form_class = ComplexObjectForm
    declared_fieldsets = [(None, {'fields': ['field1', 'nested']})]
    
    def get_extra_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = patterns('',
            url('complexone/$', SubComplexOneView.as_view(**{'admin':self, 'admin_site':self.admin_site}), name='admin_books_complex_one'),
            url('complextwo/$', SubComplexTwoView.as_view(**{'admin':self, 'admin_site':self.admin_site}), name='admin_books_complex_two'),
        )
        return urls


admin.site.register([ComplexObject], ComplexObjectAdmin)

