from django.utils import unittest

from common import SimpleDocument

from dockit.backends import CompositeIndexRouter

class RouterTestCase(unittest.TestCase):
    def setUp(self):
        self.router = CompositeIndexRouter([])
    
    def test_get_effective_query_index(self):
        queryset = SimpleDocument.objects.filter(featured=True).exclude(published=False).index('charfield')
        self.router.register_queryset(queryset)
        
        found_queryset = self.router.get_effective_queryset(queryset)['queryset']
        self.assertEqual(queryset, found_queryset)

