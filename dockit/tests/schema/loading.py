from dockit.schema.loading import get_base_document, cache as app_cache

from django.utils import unittest

from common import SimpleDocument

class LoadingTestCase(unittest.TestCase):
    def test_document_was_registered(self):
        self.assertTrue(SimpleDocument._meta.collection in app_cache.documents)
        get_base_document(SimpleDocument._meta.collection)

