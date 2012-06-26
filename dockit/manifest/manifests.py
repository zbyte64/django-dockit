from common import Manifest

from django.core import serializers as django_serializers
from dockit.core import serializers as dockit_serializers

class DjangoFixtureManifest(Manifest):
    def load(self):
        results = list()
        for data_source in self.data_sources:
            data = data_source.get_data()
            for obj in django_serializers.deserialize('python', data):
                obj.save()
                results.append(obj)
        return results

class DockitFixtureManifest(Manifest):
    def load(self):
        results = list()
        for data_source in self.data_sources:
            data = data_source.get_data()
            for obj in dockit_serializers.deserialize('python', data):
                obj.save()
                results.append(obj)
        return results

