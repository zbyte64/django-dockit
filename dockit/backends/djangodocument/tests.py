from django.utils import unittest

from dockit import backends
from dockit import schema

from models import RegisteredIndex, RegisteredIndexDocument, StringIndex

class Book(schema.Document):
    title = schema.CharField()
    slug = schema.SlugField()
    published = schema.BooleanField()
    featured = schema.BooleanField()
    countries = schema.ListField(schema.CharField())
    number_list = schema.ListField(schema.IntegerField())

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
        RegisteredIndex.objects.all().delete()
    
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
        query_hash = queryset._index_hash()
        self.assertTrue(Book._meta.collection in backends.INDEX_ROUTER.registered_querysets)
        self.assertTrue(query_hash in backends.INDEX_ROUTER.registered_querysets[Book._meta.collection], str(backends.INDEX_ROUTER.registered_querysets[Book._meta.collection]))
        self.assertTrue(RegisteredIndex.objects.filter(query_hash=query_hash, collection=Book._meta.collection).exists())
        
        book = Book(title='test title', slug='test')
        book.save()
        
        self.assertTrue(RegisteredIndexDocument.objects.filter(doc_id=book.pk, index__query_hash=query_hash).exists())
        
        self.assertTrue(StringIndex.objects.filter(value='test', param_name='slug', document__doc_id=book.pk, document__index__query_hash=query_hash).exists())
        
        vquery = RegisteredIndexDocument.objects.filter(doc_id=book.pk, index__query_hash=query_hash, index__collection=Book._meta.collection,
                                                        stringindex__param_name='slug', stringindex__value='test')
        self.assertTrue(vquery.exists())
        
        query = Book.objects.all().filter(slug='test')
        msg = str(query.queryset.query.queryset.query)
        self.assertEqual(len(list(query)), query.count())
        self.assertEqual(query.count(), 1, '%s != %s' % (msg, vquery.query))
        book.delete()
        self.assertEqual(Book.objects.all().filter(slug='test').count(), 0)
    
    def test_sparse_document_index(self):
        queryset = Book.objects.filter(featured=True).exclude(published=False).index('slug')
        queryset.commit()
        query_hash = queryset._index_hash()
        self.assertTrue(Book._meta.collection in backends.INDEX_ROUTER.registered_querysets)
        self.assertTrue(query_hash in backends.INDEX_ROUTER.registered_querysets[Book._meta.collection], str(backends.INDEX_ROUTER.registered_querysets[Book._meta.collection]))
        self.assertTrue(RegisteredIndex.objects.filter(query_hash=query_hash, collection=Book._meta.collection).exists())
        
        book = Book(title='test title', slug='test', featured=True, published=True)
        book.save()
        book2 = Book(title='test title2', slug='test2', featured=False, published=True)
        book2.save()
        
        self.assertTrue(RegisteredIndexDocument.objects.filter(doc_id=book.pk, index__query_hash=query_hash).exists())
        self.assertTrue(StringIndex.objects.filter(value='test', param_name='slug', document__doc_id=book.pk, document__index__query_hash=query_hash).exists())
        
        query = Book.objects.all().filter(featured=True).exclude(published=False)
        msg = str(query.queryset.query.queryset.query)
        self.assertEqual(query.count(), 1, msg)
        
        book.delete()
        query = Book.objects.all().filter(featured=True).exclude(published=False)
        self.assertEqual(query.count(), 0)
    
    def test_multi_value_index(self):
        queryset = Book.objects.index('countries')
        queryset.commit()
        queryset = Book.objects.index('number_list')
        queryset.commit()
        
        query = Book.objects.filter(countries="US")
        self.assertEqual(query.count(), 0)
        
        book = Book(title='test title', slug='test', featured=True, published=True, countries=['US', 'GB'])
        book.save()
        book = Book(title='test title2', slug='test2', featured=True, published=True, number_list=[1,5])
        book.save()
        
        query = Book.objects.filter(countries="US")
        self.assertEqual(query.count(), 1)

