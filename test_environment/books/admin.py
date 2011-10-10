from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin
#from dockit.admin.views import SchemaFieldView, SchemaListFieldView
from dockit.forms import DocumentForm

from models import Book, Publisher, Address, ComplexObject, SubComplexOne, SubComplexTwo

class BookAdmin(DocumentAdmin):
    pass

from django import forms

class PublisherAdmin(DocumentAdmin):
    pass

admin.site.register([Book], BookAdmin)
admin.site.register([Publisher], PublisherAdmin)

class ComplexObjectAdmin(DocumentAdmin):
    pass

admin.site.register([ComplexObject], ComplexObjectAdmin)

