from dockit import schema
from dockit import backends

from django.utils import unittest

from mock import Mock, patch

class SimpleSchema(schema.Schema): #TODO make a more complex testcase
    charfield = schema.CharField()

class SimpleDocument(schema.Document): #TODO make a more complex testcase
    charfield = schema.CharField()
    published = schema.BooleanField()
    featured = schema.BooleanField()

class BackendTestCase(unittest.TestCase):
    backend_name = None
    
    def setUp(self):
        self.patchers = list()
        
        if self.backend_name not in backends.get_document_backends():
            self.skipTest('Backend %s is not enabled' % self.backend_name)
        
        def return_backend_name(*args, **kwargs):
            return self.backend_name
        
        mock = Mock(side_effect=return_backend_name)
        self.patchers.append(patch.object(backends.DOCUMENT_ROUTER, 'get_storage_name_for_read', mock))
        self.patchers.append(patch.object(backends.DOCUMENT_ROUTER, 'get_storage_name_for_write', mock))
        
        self.patchers.append(patch.object(backends.INDEX_ROUTER, 'get_index_name_for_write', mock))
        self.patchers.append(patch.object(backends.INDEX_ROUTER, 'get_index_name_for_write', mock))
        
        self.mock_classes = list()
        for patcher in self.patchers:
            self.mock_classes.append(patcher.start())
    
    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
