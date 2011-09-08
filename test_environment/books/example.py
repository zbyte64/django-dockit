from models import Author, Book
from django.contrib.auth.models import User

user = User.objects.all()[0]
'''
author = Author(user=user)
author.save()

book = Book(title='Of Mice and Men', author=author)
book.save()
'''

for book in Book.root_index():
    print book._primitive_data
    book.tags.append('historical')
    book.save()
    print book._primitive_data
