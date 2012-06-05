from django.utils import unittest

from common import SimpleDocument

from dockit.backends import CompositeIndexRouter

class RouterTestCase(unittest.TestCase):
    def setUp(self):
        self.router = CompositeIndexRouter([])
    
    def test_get_effective_query_index(self):
        original_queryset = SimpleDocument.objects.filter(featured=True).exclude(published=False).index('charfield')
        self.router.register_queryset(original_queryset)
        
        #create a new queryset object
        sub_queryset = SimpleDocument.objects.filter(featured=True).exclude(published=False)
        
        found_queryset = self.router.get_effective_queryset(sub_queryset)['queryset']
        self.assertEqual(original_queryset._index_hash(), found_queryset._index_hash())

