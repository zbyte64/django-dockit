from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin
#from dockit.admin.views import SchemaFieldView, SchemaListFieldView

from models import Book, Publisher, Author, Address, ComplexObject, SubComplexOne, SubComplexTwo

class BookAdmin(DocumentAdmin):
    pass

class PublisherAdmin(DocumentAdmin):
    pass

class AuthorAdmin(DocumentAdmin):
    pass

admin.site.register([Book], BookAdmin)
admin.site.register([Publisher], PublisherAdmin)
admin.site.register([Author], AuthorAdmin)

class ComplexObjectAdmin(DocumentAdmin):
    pass

admin.site.register([ComplexObject], ComplexObjectAdmin)

