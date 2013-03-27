from dockit.schema.loading import get_base_document, cache as app_cache, force_register_documents
from dockit.schema.schema import create_document
from dockit import schema

from django.utils import unittest

from dockit.tests.schema.common import SimpleDocument


class LoadingTestCase(unittest.TestCase):
    def test_document_was_registered(self):
        self.assertTrue(SimpleDocument._meta.collection in app_cache.documents)
        get_base_document(SimpleDocument._meta.collection)
    
    def test_force_register_documents(self):
        doc = create_document('testDocument', fields={'title':schema.CharField()})
        
        doc = create_document('testDocument', fields={'title':schema.CharField(), 'slug':schema.SlugField()})
        force_register_documents(doc._meta.app_label, doc)
        
        doc = get_base_document(doc._meta.collection)
        
        self.assertTrue('slug' in doc._meta.fields)

