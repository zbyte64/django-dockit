from django.utils import unittest

from dockit import schema
from dockit.datataps import DocumentDataTap


class SimpleDocument(schema.Document):
    charfield = schema.CharField()
    published = schema.BooleanField()
    featured = schema.BooleanField()

class DocumentDataTapTestCase(unittest.TestCase):
    def test_write_item(self):
        tap = DocumentDataTap()
        tap.open('w')
        result = tap.write_item({
            'collection': SimpleDocument._meta.collection,
            'fields': {
                'charfield': 'testchar',
                'published': True,
                'featured': False,
            }
        })
        self.assertTrue(isinstance(result, SimpleDocument))
        tap.close()
    
    def test_get_item_stream(self):
        SimpleDocument.objects.all().delete()
        SimpleDocument(charfield='testchar').save()
        
        tap = DocumentDataTap(SimpleDocument)
        tap.open('r')
        items = list(tap.get_item_stream())
        self.assertTrue(items)
        self.assertEqual(len(items), SimpleDocument.objects.all().count())
        assert len(items)
        tap.close()

