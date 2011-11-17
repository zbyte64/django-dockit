import dockit

from django.contrib.auth.models import User

class Author(dockit.Document):
    collection = 'author'
    
    user = dockit.ModelReferenceField(User)
    internal_id = dockit.TextField()

class Address(dockit.Schema):
    street_1 = dockit.TextField()
    street_2 = dockit.TextField(blank=True)
    city = dockit.TextField()
    postal_code = dockit.TextField()
    region = dockit.TextField()
    country = dockit.TextField()
    
    extra_data = dockit.DictField(blank=True)

class Publisher(dockit.Document):
    collection = 'publisher'
    
    name = dockit.TextField()
    address = dockit.SchemaField(Address)
    
    def __unicode__(self):
        return self.name

class Book(dockit.Document):
    collection = 'book'
    
    title = dockit.TextField()
    cover_image = dockit.FileField(upload_to='book-images')
    year = dockit.IntegerField()
    publisher = dockit.ReferenceField(Publisher)
    authors = dockit.ListField(dockit.ReferenceField(Author), db_index=True)
    tags = dockit.ListField(dockit.TextField(), db_index=True)

class SubComplexTwo(dockit.Schema):
    field2 = dockit.TextField()

class SubComplexOne(dockit.Schema):
    field1 = dockit.TextField()
    nested = dockit.SchemaField(SubComplexTwo)

class ComplexObject(dockit.Document):
    collection = 'complex_object'
    
    field1 = dockit.TextField()
    image = dockit.FileField(upload_to='complex-images', blank=True)
    addresses = dockit.ListField(dockit.SchemaField(Address), blank=True)
    main_address = dockit.SchemaField(Address, blank=True)
    
    nested = dockit.SchemaField(SubComplexOne, blank=True)
