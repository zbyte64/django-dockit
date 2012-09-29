from dockit.manifest.adaptors import JSONAdaptor
from dockit.manifest.datasources import InlineDataSource

from django.utils import unittest

class JSONAdaptorTestCase(unittest.TestCase):
    def test_deserialize(self):
        data = JSONAdaptor().deserialize(InlineDataSource(), '{"foo": "bar"}')
        self.assertEqual(data, {'foo':'bar'})
