from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin

from models import Book, Publisher

class BookAdmin(DocumentAdmin):
    pass

class PublisherAdmin(DocumentAdmin):
    pass

admin.site.register([Book], BookAdmin)
admin.site.register([Publisher], PublisherAdmin)
