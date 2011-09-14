import dockit

from django.contrib.auth.models import User

class Author(dockit.Document):
    collection = 'author'
    
    user = dockit.ModelReferenceField(User)

class Address(dockit.Schema):
    street_1 = dockit.TextField()
    street_2 = dockit.TextField()
    city = dockit.TextField()
    postal_code = dockit.TextField()
    region = dockit.TextField()
    country = dockit.TextField()

class Publisher(dockit.Document):
    collection = 'publisher'
    
    name = dockit.TextField()
    address = dockit.SchemaField(Address)

class Book(dockit.Document):
    collection = 'book'
    
    title = dockit.TextField()
    year = dockit.IntegerField()
    publisher = dockit.ReferenceField(Publisher)
    authors = dockit.ListField(dockit.ReferenceField(Author), db_index=True)
    tags = dockit.ListField(dockit.TextField(), db_index=True)

