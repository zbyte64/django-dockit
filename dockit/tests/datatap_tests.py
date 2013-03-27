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

from tempfile import mkstemp
import zipfile
import json

from datatap.management.commands import datatap


class DocumentToZipCommandIntregrationTestCase(unittest.TestCase):
    def test_dumpdatatap(self):
        SimpleDocument(charfield='testchar').save()
        filename = mkstemp('zip', 'datataptest')[1]
        cmd = datatap.Command()
        argv = ['manage.py', 'datatap', 'Document', SimpleDocument._meta.collection, '--', 'ZipFile', '--file', filename]
        cmd.run_from_argv(argv)
        
        archive = zipfile.ZipFile(filename)
        self.assertTrue('manifest.json' in archive.namelist())
        manifest = json.load(archive.open('manifest.json', 'r'))
        self.assertEqual(len(manifest), SimpleDocument.objects.all().count())
    
    def test_loaddatatap(self):
        SimpleDocument.objects.all().delete()
        item = {
            'collection': SimpleDocument._meta.collection,
            'fields': {
                'charfield': 'testchar',
                'published': True,
                'featured': False,
            }
        }
        filename = mkstemp('zip', 'datataptest')[1]
        archive = zipfile.ZipFile(filename, 'w')
        archive.writestr('manifest.json', json.dumps([item]))
        archive.writestr('originator.txt', 'Document')
        archive.close()
        
        cmd = datatap.Command()
        argv = ['manage.py', 'datatap', 'ZipFile', '--file', filename]
        cmd.run_from_argv(argv)
        
        result = SimpleDocument.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].charfield, 'testchar')
