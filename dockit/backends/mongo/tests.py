from django.utils import unittest

from dockit import schema
from dockit import backends
from dockit.models import TemporaryDocument

class TestDocument(TemporaryDocument):
    charfield = schema.CharField()
    listfield = schema.ListField(schema.CharField())

class MockedDocumentRouter(backends.CompositeDocumentRouter):
    def __init__(self):
        super(MockedDocumentRouter, self).__init__([])
    
    def get_storage_name_for_read(self, document):
        return 'mongo'
    
    def get_storage_name_for_write(self, document):
        return 'mongo'

class MockedIndexRouter(backends.CompositeIndexRouter):
    def __init__(self):
        super(MockedIndexRouter, self).__init__([])
    
    def get_index_name_for_read(self, document, queryset):
        return 'mongo'
    
    def get_index_name_for_write(self, document, queryset):
        return 'mongo'

class MongoBackendTestCase(unittest.TestCase):
    def setUp(self):
        #TODO use mock instead
        self._original_document_router = backends.DOCUMENT_ROUTER
        self._original_index_router = backends.INDEX_ROUTER
        
        backends.DOCUMENT_ROUTER = MockedDocumentRouter()
        backends.INDEX_ROUTER = MockedIndexRouter()
        
        TestDocument.objects.all().delete()
    
    def tearDown(self):
        backends.DOCUMENT_ROUTER = self._original_document_router
        backends.INDEX_ROUTER = self._original_index_router
    
    def test_get_nonexistant_document_raises_error(self):
        try:
            TestDocument.objects.get(pk=None)
        except TestDocument.DoesNotExist:
            pass
        else:
            self.fail('Retrieved non-existant document')
        
        try:
            TestDocument.objects.get(pk='3f32ea6fd946e17d44000000')
        except TestDocument.DoesNotExist:
            pass
        else:
            self.fail('Retrieved non-existant document')
    
    def test_create_document(self):
        doc = TestDocument(charfield='test')
        doc.save()
        
        doc2 = TestDocument.objects.get(pk=doc.pk)
        self.assertEqual(doc, doc2)
        self.assertEqual(doc.charfield, doc2.charfield)
    
    def test_delete_document(self):
        doc = TestDocument(charfield='test')
        doc.save()
        pk = doc.pk
        doc.delete()
        try:
            doc2 = TestDocument.objects.get(pk=pk)
        except TestDocument.DoesNotExist:
            pass
        else:
            self.fail('Document was not deleted')
    
    def test_update_document(self):
        doc = TestDocument(charfield='test')
        doc.save()
        
        doc.charfield = 'test2'
        doc.listfield = ['a', 'b', 'c']
        doc.save()
        
        doc2 = TestDocument.objects.get(pk=doc.pk)
        self.assertEqual(doc.listfield, doc2.listfield)
    
    def test_document_index(self):
        queryset = TestDocument.objects.index('charfield')
        queryset.commit()
        self.assertTrue(TestDocument._meta.collection in backends.INDEX_ROUTER.registered_querysets)
        self.assertTrue(queryset._index_hash() in backends.INDEX_ROUTER.registered_querysets[TestDocument._meta.collection], str(backends.INDEX_ROUTER.registered_querysets[TestDocument._meta.collection]))
        
        doc = TestDocument(charfield='test')
        doc.save()
        self.assertEqual(TestDocument.objects.all().filter(charfield='test').count(), 1)
        doc.delete()
        self.assertEqual(TestDocument.objects.all().filter(charfield='test').count(), 0)

