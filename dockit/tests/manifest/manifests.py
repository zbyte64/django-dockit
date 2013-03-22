from dockit.manifest.manifests import DjangoFixtureManifest, DockitFixtureManifest
from dockit.manifest.datasources import InlineDataSource
from dockit.manifest.common import ManifestLoader

from django.utils import unittest

class ManifestTestCase(unittest.TestCase):
    def setUp(self):
        self.manifest_loader = ManifestLoader(manifests={'djangofixture':DjangoFixtureManifest,
                                                         'dockitfixture':DockitFixtureManifest,},
                                              data_sources={'inline':InlineDataSource})
    
    def test_load_dockitfixture_manifest(self):
        data = {'loader':'dockitfixture',
                'data':[{'source':'inline',
                         'data':[{
                             "collection":"dockit.temporarydocument",
                             "pk": 1,
                             "natural_key": {"pk":1},
                             "fields": {
                                 "_tempinfo": {
                                    "user": None,
                                 },
                                 "extrafield": 1,
                             }
                         }],
                       }]
               }
        manifest = self.manifest_loader.load_manifest(data)
        objects = manifest.load()
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].object['extrafield'], 1)
    
    def test_load_djangofixture_manifest(self):
        data = {'loader':'djangofixture',
                'data':[{'source':'inline',
                         'data':[{
                             "model": "auth.user",
                             "pk": 1,
                             "fields": {
                                 "username": "fixtureuser",
                                 "first_name": "John",
                                 "last_name": "Lennon",
                                 "email": "z@z.com",
                             }
                          }],
                       }]
               }
        manifest = self.manifest_loader.load_manifest(data)
        objects = manifest.load()
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].object.username, 'fixtureuser')
    
    def test_create_dockitfixture_manifest(self):
        from dockit.models import TemporaryDocument
        foo = TemporaryDocument(extrafield=1)
        data_sources = [(InlineDataSource, [foo], {})]
        payload = self.manifest_loader.create_manifest_payload('dockitfixture', data_sources)
        self.assertEqual(len(payload['data']), 1)

