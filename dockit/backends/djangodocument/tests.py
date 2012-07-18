from django.utils import unittest
from django.contrib.sites.models import Site

from dockit import backends
from dockit import schema
from dockit.tests.backends.common import BackendTestCase

from models import RegisteredIndex, RegisteredIndexDocument, StringIndex

class Book(schema.Document):
    title = schema.CharField()
    slug = schema.SlugField()
    published = schema.BooleanField()
    featured = schema.BooleanField()
    countries = schema.ListField(schema.CharField())
    number_list = schema.ListField(schema.IntegerField())
    sites = schema.ModelSetField(Site)

class DjangoDocumentTestCase(BackendTestCase):
    backend_name = 'djangodocument'
    
    def setUp(self):
        super(DjangoDocumentTestCase, self).setUp()
        
        self.clear_books()
        RegisteredIndex.objects.all().delete()
    
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
        
        #TODO these are more of a queryindex test
        Book.objects.get(slug='test')
        Book.objects.get(pk=book.pk)
        
        try:
            bad_book = Book.objects.get(pk=int(book.pk)+500)
        except Book.DoesNotExist:
            pass
        else:
            self.fail('Pk lookup of non-existant object returned an object: %s' % bad_book)
        
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
        queryset = Book.objects.index('sites')
        queryset.commit()
        
        query = Book.objects.filter(countries="US")
        self.assertEqual(query.count(), 0)
        
        book = Book(title='test title', slug='test', featured=True, published=True, countries=['US', 'GB'], sites=[Site.objects.get_current()])
        book.save()
        ibook = Book(title='test title2', slug='test2', featured=True, published=True, number_list=[1,5])
        ibook.save()
        
        query = Book.objects.filter(countries="US")
        self.assertEqual(query.count(), 1)
        
        query = Book.objects.filter(sites=Site.objects.get_current().pk)
        self.assertEqual(query.count(), 1)
        self.assertEqual(query[0].pk, book.pk)
        
        query = Book.objects.filter(sites=Site.objects.get_current())
        self.assertEqual(query.count(), 1)
    
    def test_stale_index(self):
        RegisteredIndex.objects.create(query_hash=0, collection=Book._meta.collection)
        RegisteredIndex.objects.on_save(Book._meta.collection, 127, {})
        
        backends.INDEX_ROUTER.registered_querysets[Book._meta.collection] = {}
        RegisteredIndex.objects.on_save(Book._meta.collection, 127, {})
    
    def test_natural_key_index(self):
        queryset = Book.objects.index('@natural_key_hash__exact')
        queryset.commit()
        
        ibook = Book(title='test title2', slug='test2', featured=True, published=True, number_list=[1,5])
        ibook.save()
        
        self.assertEqual(queryset.count(), 1)
        
        ibook2 = Book.objects.natural_key(**ibook.natural_key)
        
        self.assertEqual(ibook, ibook2)

