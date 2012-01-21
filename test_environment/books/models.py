import dockit

from django.contrib.auth.models import User

class Author(dockit.Document):
    user = dockit.ModelReferenceField(User)
    internal_id = dockit.TextField()
    
    class Meta:
        collection = 'author'

class Address(dockit.Schema):
    street_1 = dockit.TextField()
    street_2 = dockit.TextField(blank=True)
    city = dockit.TextField()
    postal_code = dockit.TextField()
    region = dockit.TextField()
    country = dockit.TextField()
    
    extra_data = dockit.DictField(blank=True)

class Publisher(dockit.Document):
    name = dockit.TextField()
    address = dockit.SchemaField(Address)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        collection = 'publisher'

class Book(dockit.Document):
    title = dockit.TextField()
    cover_image = dockit.FileField(upload_to='book-images')
    year = dockit.IntegerField()
    publisher = dockit.ReferenceField(Publisher)
    authors = dockit.ListField(dockit.ReferenceField(Author), db_index=True)
    tags = dockit.ListField(dockit.TextField(), db_index=True)
    
    class Meta:
        collection = 'book'

Book.objects.enable_index("equals", "tags", {'field':'tags'})

class SubComplexTwo(dockit.Schema):
    field2 = dockit.TextField()

class SubComplexOne(dockit.Schema):
    field1 = dockit.TextField()
    nested = dockit.SchemaField(SubComplexTwo)

class ComplexObject(dockit.Document):
    field1 = dockit.TextField()
    image = dockit.FileField(upload_to='complex-images', blank=True)
    addresses = dockit.ListField(dockit.SchemaField(Address), blank=True)
    main_address = dockit.SchemaField(Address, blank=True)
    generic_objects = dockit.ListField(dockit.GenericSchemaField(), blank=True)
    
    nested = dockit.SchemaField(SubComplexOne, blank=True)
    
    def __unicode__(self):
        return unicode(self.field1)
    
    class Meta:
        collection = 'complex_object'
