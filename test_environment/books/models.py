import dockit

from django.contrib.auth.models import User

class Author(dockit.Document):
    collection = 'author'
    
    user = dockit.ModelReferenceField(User)

class Book(dockit.Document):
    collection = 'book'
    
    title = dockit.TextField()
    year = dockit.IntegerField()
    author = dockit.ReferenceField(Author)


