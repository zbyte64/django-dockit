from django.utils import unittest

from common import SimpleDocument

from dockit.backends import CompositeIndexRouter
from dockit import backends

class RouterTestCase(unittest.TestCase):
    def setUp(self):
        self.router = backends.INDEX_ROUTER#CompositeIndexRouter([])
        
    
    def test_get_effective_query_index(self):
        original_queryset = SimpleDocument.objects.filter(featured=True).exclude(published=False).index('charfield')
        self.router.register_queryset(original_queryset)
        
        #create a new queryset object
        sub_queryset = SimpleDocument.objects.filter(featured=True).exclude(published=False)
        
        result = self.router.get_effective_queryset(sub_queryset)
        self.assertFalse(result['inclusions']) #no extra inclusions or exclusions should be necessary
        self.assertFalse(result['exclusions'])
        self.assertEqual(original_queryset._index_hash(), result['queryset']._index_hash())

