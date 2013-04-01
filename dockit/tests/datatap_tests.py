from django.utils import unittest

from datatap.datataps import MemoryDataTap

from dockit import schema
from dockit.datataps import DocumentDataTap


class SimpleDocument(schema.Document):
    charfield = schema.CharField()
    published = schema.BooleanField()
    featured = schema.BooleanField()

class DocumentDataTapTestCase(unittest.TestCase):
    def test_load_item(self):
        SimpleDocument.objects.all().delete()
        source = MemoryDataTap([{
            'collection': SimpleDocument._meta.collection,
            'fields': {
                'charfield': 'testchar',
                'published': True,
                'featured': False,
            }
        }])
        tap = DocumentDataTap(instream=source)
        result = list(tap)
        self.assertTrue(len(result), 1)
        self.assertTrue(hasattr(result[0], 'save'))
        tap.commit() #this saves said objects
        tap.close()
        self.assertEqual(SimpleDocument.objects.all().count(), 1)
    
    def test_get_item_stream(self):
        SimpleDocument.objects.all().delete()
        SimpleDocument(charfield='testchar').save()
        
        tap = DocumentDataTap(instream=[SimpleDocument])
        items = list(tap)
        self.assertTrue(items)
        self.assertEqual(len(items), SimpleDocument.objects.all().count())
        assert len(items)
        tap.close()

from tempfile import mkstemp
import zipfile
import json

from datatap.management.commands import datatap


class DocumentToZipCommandIntregrationTestCase(unittest.TestCase):
    def test_document_to_zipfile(self):
        SimpleDocument(charfield='testchar').save()
        filename = mkstemp('zip', 'datataptest')[1]
        cmd = datatap.Command()
        argv = ['manage.py', 'datatap', 'Document', SimpleDocument._meta.collection, '--', 'Zip', '--', 'File', filename]
        cmd.run_from_argv(argv)
        
        archive = zipfile.ZipFile(filename)
        self.assertTrue('manifest.json' in archive.namelist())
        manifest = json.load(archive.open('manifest.json', 'r'))
        self.assertEqual(len(manifest), SimpleDocument.objects.all().count())
    
    def test_zipfile_to_document(self):
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
        argv = ['manage.py', 'datatap', 'File', filename, '--', 'Zip', '--', 'Document']
        cmd.run_from_argv(argv)
        
        result = SimpleDocument.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].charfield, 'testchar')

