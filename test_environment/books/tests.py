from django.utils import unittest
from django.contrib.auth.models import User

from models import Author, Book, Publisher, Address

class BookTestCase(unittest.TestCase):

    def test_monolithic(self):
        user = User.objects.create_user(username='test', email='z@z.com')
        addr = Address(street_1='10533 Reagan Rd', city='San Diego', postal_code='92126', country='US', region='CA')

        author = Author(user=user)
        author.save()

        publisher = Publisher(name='Books etc', address=addr)
        publisher.save()

        book = Book(title='Of Mice and Men', publisher=publisher)
        book.authors.append(author)
        book.save()
        book.tags.append('historical')
        book.save()

        book = Book.load(book.get_id())
        assert 'historical' in book.tags
        assert book.title == 'Of Mice and Men'
        assert book.publisher.name == 'Books etc'
        assert book.publisher.address.city == 'San Diego'
        assert book.authors[0].user
        
        #test that modifying a nested schema is preserved
        publisher.address.street_2 = 'Apt 1'
        publisher.save()
        
        publisher = Publisher.load(publisher.get_id())
        
        assert publisher.address.street_2 == 'Apt 1'
    
    def test_admin(self):
        import admin
