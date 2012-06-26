from dockit.manifest.adaptors import JSONAdaptor

from django.utils import unittest

class JSONAdaptorTestCase(unittest.TestCase):
    def test_deserialize(self):
        data = JSONAdaptor().deserialize('{"foo": "bar"}')
        self.assertEqual(data, {'foo':'bar'})
