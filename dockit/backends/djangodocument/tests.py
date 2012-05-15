from django.utils import unittest

from dockit import backends
from dockit import schema

class Book(schema.Document):
    title = schema.CharField()
    slug = schema.SlugField()

class DjangoDocumentTestCase(unittest.TestCase):
    def setUp(self):
        self._original_backend = backends.backends['default']
        backends.backends['default'] = self._create_backend()
        self.backend = backends.backends['default']()
        self.clear_books()
    
    def clear_books(self):
        Book.objects.all().delete()
    
    def tearDown(self):
        backends.backends['default'] = self._original_backend
    
    def _create_backend(self):
        return backends.backends['djangodocument']
    
    def test_document_store(self):
        self.assertEqual(Book.objects.all().count(), 0)
        Book(title='test title', slug='test').save()
        self.assertEqual(Book.objects.all().count(), 1)
        book = Book.objects.all()[0]
        self.assertEqual(book.title, 'test title')
        self.assertEqual(book.slug, 'test')
    
    def test_document_index(self):
        Book.objects.index('slug').commit()
        self.assertTrue(Book._meta.collection in self.backend.indexes)
        
        Book(title='test title', slug='test').save()
        self.assertEqual(Book.objects.all().filter(slug='test').count(), 1)

