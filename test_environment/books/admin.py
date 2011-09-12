from django.contrib import admin

from dockit.admin.documentadmin import DocumentAdmin

from models import Book

admin.site.register([Book], DocumentAdmin)
