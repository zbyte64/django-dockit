from django.utils import unittest

import dockit
from dockit import backends
from dockit.models import TemporaryDocument
from dockit.backends.mongo.backend import MongoDocumentStorage

class TestDocument(TemporaryDocument):
    charfield = dockit.CharField()
    listfield = dockit.ListField(dockit.CharField())

class MongoBackendTestCase(unittest.TestCase):
    def setUp(self):
        self._original_backend = backends.backend
        backends.backend = self._create_backend()
    
    def tearDown(self):
        backends.backend = self._original_backend
    
    def _create_backend(self):
        return MongoDocumentStorage(host='localhost', port=27017, db='testdb')
    
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

