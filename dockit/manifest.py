from django.core import serializers as django_serializers
from dockit.core import serializers as dockit_serializers

from urllib2 import urlopen

class DataAdaptor(object):
    def deserialize(self, file_obj):
        raise NotImplementedError

def get_adaptor(format):
    pass

class DataSource(object):
    def __init__(self, **options):
        self.options = options
    
    def get_data(self):
        raise NotImplementedError

class URLDataSource(DataSource):
    def __init__(self, url, **options):
        self.url = url
        super(URLDataSource, self).__init__(**options)
    
    def get_data(self):
        response = urlopen(self.url)
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(response)
        return data

class InlineDataSource(DataSource):
    def __init__(self, data, **options):
        self.data = data
        super(InlineDataSource, self).__init__(**options)
    
    def get_data(self):
        return self.data

class LocalDataSource(DataSource):
    def __init__(self, filename, **options):
        self.filename = filename
        super(LocalDataSource, self).__init__(**options)
    
    def get_file_path(self):
        #TODO return the proper filename or something
        return self.filename
    
    def get_data(self):
        path = self.get_file_path()
        source = open(path, 'r')
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(source)
        return data

class ZipfileDataSource(DataSource):
    def __init__(self, filename, archive, **options):
        self.filename = filename
        self.archive = archive
        super(ZipfileDataSource, self).__init__(**options)
    
    def get_file_path(self):
        return self.filename
    
    def get_data(self):
        path = self.get_file_path()
        source = self.archive.open(path)
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(source)
        return data

class ManifestLoader(object):
    def __init__(self, manifests, data_sources):
        self.manifests = manifests
        self.data_sources = data_sources
    
    def get_manifest_kwargs(self, **kwargs):
        return kwargs
    
    def create_manifest(self, manifest_data):
        manifest_options = dict(manifest_data)
        manifest_cls = self.manifests[manifest_options.pop('loader')]
        data_sources = list()
        for data in manifest_options.pop('data'):
            data_source = self.load_data_source(data)
            data_sources.append(data_source)
        manifest_kwargs = self.get_manifest_kwargs(data_sources=data_sources, **manifest_options)
        return manifest_cls(**manifest_kwargs)
    
    def get_data_source_kwargs(self, **kwargs):
        return kwargs
    
    def load_data_source(self, data):
        data_source_options = dict(data)
        data_source_cls = self.data_sources[data_source_options.pop('source')]
        data_source_kwargs = self.get_data_source_kwargs(**data_source_options)
        data_source = data_source_cls(**data_source_kwargs)
        return data_source

class Manifest(object):
    def __init__(self, data_sources, **options):
        self.data_sources = data_sources
        self.options = options
    
    def load(self):
        raise NotImplementedError

class DjangoFixtureManifest(Manifest):
    def load(self):
        for data_source in self.data_sources:
            data = data_source.get_data()
            obj = django_serializers.deserialize('python', data)
            obj.save()

class DockitFixtureManifest(Manifest):
    def load(self):
        for data_source in self.data_sources:
            data = data_source.get_data()
            obj = dockit_serializers.deserialize('python', data)
            obj.save()

'''
Example manifest:

{
loader: "django_fixture"
data: [
    {source:'local', format:'json', filename:'somefile.json'}, #relative to manifest source
    {source:'inline', data:[{}]}, #inline data
    {source:'url', format:'json', url:'http://www.example.com/fixture.json'}, #online data
]
}
'''
