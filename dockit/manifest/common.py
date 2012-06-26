ADAPTORS = dict()

def register_adaptor(format, cls):
    ADAPTORS[format] = cls

def get_adaptor(format):
    return ADAPTORS[format]()

class DataAdaptor(object):
    def deserialize(self, file_obj):
        raise NotImplementedError

class DataSource(object):
    def __init__(self, **options):
        self.options = options
    
    def get_data(self):
        raise NotImplementedError

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
