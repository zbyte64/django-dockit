ADAPTORS = dict()

def register_adaptor(format, cls):
    ADAPTORS[format] = cls

def get_adaptor(format):
    return ADAPTORS[format]()

class DataAdaptor(object):
    def deserialize(self, file_obj):
        raise NotImplementedError
    
    def serialize(self, python_objects):
        raise NotImplementedError

class DataSource(object):
    def __init__(self, **options):
        self.options = options
    
    def get_data(self):
        raise NotImplementedError
    
    @classmethod
    def to_payload(cls, source, data, **options):
        '''
        Returns the manifest payload representation
        '''
        raise NotImplementedError

class ManifestLoader(object):
    def __init__(self, manifests, data_sources):
        self.manifests = manifests
        self.data_sources = data_sources
    
    def get_manifest_kwargs(self, **kwargs):
        return kwargs
    
    def load_manifest(self, manifest_data):
        manifest_options = dict(manifest_data)
        manifest_cls = self.manifests[manifest_options.pop('loader')]
        manifest_kwargs = self.get_manifest_kwargs(**manifest_options)
        manifest = manifest_cls(**manifest_kwargs)
        manifest.load_data_sources(self)
        return manifest
    
    def create_manifest_payload(self, loader, data_sources):
        '''
        data_sources = [(data_source_cls, objects, options)...]
        '''
        manifest_cls = self.manifests[loader]
        payload = {'loader':loader,
                   'data':[]}
        for data_source_cls, objects, options in data_sources:
            source = None
            for key, cls in self.data_sources.iteritems():
                if data_source_cls == cls:
                    source = key
                    break
            data = manifest_cls.dump(objects)
            payload['data'].append(data_source_cls.to_payload(source, data, **options))
        return payload

class Manifest(object):
    def __init__(self, **options):
        self.options = options
    
    def parse_data_sources(self, loader, alist):
        data_sources = list()
        for data in alist:
            data_source = self.load_data_source(loader, data)
            data_sources.append(data_source)
        return data_sources
    
    def load_data_sources(self, loader):
        self.data_sources = self.parse_data_sources(loader, self.options.pop('data', []))
    
    def get_data_source_kwargs(self, **kwargs):
        return kwargs
    
    def load_data_source(self, loader, data):
        data_source_options = dict(data)
        data_source_cls = loader.data_sources[data_source_options.pop('source')]
        data_source_kwargs = self.get_data_source_kwargs(**data_source_options)
        data_source = data_source_cls(**data_source_kwargs)
        return data_source
    
    def load(self):
        '''
        Returns the loaded objects
        '''
        raise NotImplementedError
    
    @classmethod
    def dump(cls, objects):
        '''
        Returns primitive python objects that is compatible with data sources
        '''
        raise NotImplementedError

