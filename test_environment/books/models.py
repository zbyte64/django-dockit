from dockit.schema import Document, Schema, ModelReferenceField, \
    TextField, DictField, SchemaField, FileField, IntegerField, \
    ReferenceField, ListField, GenericSchemaField, CharField, DateField

from django.contrib.auth.models import User

class Author(Document):
    user = ModelReferenceField(User)
    internal_id = TextField()
    
    class Meta:
        collection = 'author'

class Address(Schema):
    street_1 = TextField()
    street_2 = TextField(blank=True)
    city = TextField()
    postal_code = TextField()
    region = TextField()
    country = TextField()
    
    extra_data = DictField(blank=True)

class Publisher(Document):
    name = TextField()
    address = SchemaField(Address)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        collection = 'publisher'

class Book(Document):
    title = TextField()
    cover_image = FileField(upload_to='book-images')
    year = IntegerField()
    publisher = ReferenceField(Publisher)
    authors = ListField(ReferenceField(Author), db_index=True)
    tags = ListField(TextField(), db_index=True)
    
    class Meta:
        collection = 'book'

Book.objects.index('tags').commit()

class SubComplexTwo(Schema):
    field2 = TextField()

class SubComplexOne(Schema):
    field1 = TextField()
    nested = SchemaField(SubComplexTwo)

class ComplexObject(Document):
    field1 = TextField()
    image = FileField(upload_to='complex-images', blank=True)
    addresses = ListField(SchemaField(Address), blank=True)
    main_address = SchemaField(Address, blank=True)
    generic_objects = ListField(GenericSchemaField(), blank=True)
    
    nested = SchemaField(SubComplexOne, blank=True)
    
    def __unicode__(self):
        return unicode(self.field1)
    
    class Meta:
        collection = 'complex_object'

class Publication(Document):
    name = CharField()
    date = DateField()
    
    class Meta:
        typed_field = '_type'

class Newspaper(Publication):
    city = CharField()
    
    class Meta:
        typed_key = 'newspaper'

class Magazine(Publication):
    issue_number = CharField()
    
    class Meta:
        typed_key = 'magazine'

class BaseProduct(Document):
    name = CharField()
    
    class Meta:
        typed_field = '_type'

class Brand(Document):
    name = CharField()
    products = ListField(SchemaField(BaseProduct))

class Shoes(BaseProduct):
    class Meta:
        typed_key = 'shoes'

class Shirt(BaseProduct):
    class Meta:
        typed_key = 'shirt'

