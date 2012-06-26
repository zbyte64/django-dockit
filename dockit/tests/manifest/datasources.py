from dockit.manifest.datasources import InlineDataSource

from django.utils import unittest

class InlineDataSourceTestCase(unittest.TestCase):
    def test_get_data(self):
        data_source = InlineDataSource(data=[])
        self.assertEqual(data_source.get_data(), [])
