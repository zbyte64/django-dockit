from django.utils import unittest

from dockit import backends
from dockit import schema

class Book(schema.Document):
    title = schema.CharField()
    slug = schema.SlugField()

class MockedDocumentRouter(backends.CompositeDocumentRouter):
    def __init__(self):
        super(MockedDocumentRouter, self).__init__([])
    
    def get_storage_name_for_read(self, document):
        return 'djangodocument'
    
    def get_storage_name_for_write(self, document):
        return 'djangodocument'

class MockedIndexRouter(backends.CompositeIndexRouter):
    def __init__(self):
        super(MockedIndexRouter, self).__init__([])
    
    def get_index_name_for_read(self, document, queryset):
        return 'djangodocument'
    
    def get_index_name_for_write(self, document, queryset):
        return 'djangodocument'

class DjangoDocumentTestCase(unittest.TestCase):
    def setUp(self):
        #TODO use mock instead
        self._original_document_router = backends.DOCUMENT_ROUTER
        self._original_index_router = backends.INDEX_ROUTER
        
        backends.DOCUMENT_ROUTER = MockedDocumentRouter()
        backends.INDEX_ROUTER = MockedIndexRouter()
        self.clear_books()
    
    def tearDown(self):
        backends.DOCUMENT_ROUTER = self._original_document_router
        backends.INDEX_ROUTER = self._original_index_router
    
    def clear_books(self):
        Book.objects.all().delete()
    
    def test_document_store(self):
        self.assertEqual(Book.objects.all().count(), 0)
        Book(title='test title', slug='test').save()
        self.assertEqual(Book.objects.all().count(), 1)
        book = Book.objects.all()[0]
        self.assertEqual(book.title, 'test title')
        self.assertEqual(book.slug, 'test')
    
    def test_document_index(self):
        queryset = Book.objects.index('slug')
        queryset.commit()
        self.assertTrue(Book._meta.collection in backends.INDEX_ROUTER.registered_querysets)
        self.assertTrue(queryset._index_hash() in backends.INDEX_ROUTER.registered_querysets[Book._meta.collection], str(backends.INDEX_ROUTER.registered_querysets[Book._meta.collection]))
        
        book = Book(title='test title', slug='test')
        book.save()
        self.assertEqual(Book.objects.all().filter(slug='test').count(), 1)
        book.delete()
        self.assertEqual(Book.objects.all().filter(slug='test').count(), 0)

