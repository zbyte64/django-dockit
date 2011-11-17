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

        book = Book.objects.get(book.get_id())
        assert 'historical' in book.tags
        self.assertEqual(book.title, 'Of Mice and Men')
        self.assertEqual(book.publisher.name, 'Books etc')
        self.assertEqual(book.publisher.address.city, 'San Diego')
        assert book.authors[0].user
        
        #test that modifying a nested schema is preserved
        publisher.address.street_2 = 'Apt 1'
        publisher.save()
        
        publisher = Publisher.objects.get(publisher.get_id())
        
        self.assertEqual(publisher.address.street_2, 'Apt 1')
        
        book = Book.objects.filter(tags='historical')[0]
        self.assertEqual(book.title, 'Of Mice and Men')
        
        self.assertEqual(Book.objects.filter(tags='fiction').count(), 0)
        
        self.assertEqual(publisher.dot_notation('address.country'), 'US')
        
        publisher.dot_notation_to_field('address')
        
        publisher.dot_notation_set_value('address.street_2', '# 1')
        self.assertEqual(publisher.address.street_2, '# 1')
        
        book.dot_notation_set_value('authors.0.internal_id', 'foo')
        self.assertEqual(book.authors[0].internal_id, 'foo')
    
    def test_admin(self):
        import admin
