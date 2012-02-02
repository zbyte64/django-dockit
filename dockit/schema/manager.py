from copy import copy

class MethodProxy(object):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute
    
    def __call__(self, *args, **kwargs):
        return getattr(self.obj, self.attribute)(*args, **kwargs)

class DictObjectMethodProxy(object):
    def __init__(self, dct, attribute):
        self._dct = dct
        self._attribute = attribute
    
    def __getattribute__(self, key):
        dct = object.__getattribute__(self, '_dct')
        if key in dct:
            return MethodProxy(dct[key], object.__getattribute__(self, '_attribute'))
        return object.__getattribute__(self, key)

class IndexManager(object):
    def __init__(self, schema):
        self.schema = schema
        self._indexes = dict()
        self.filter = DictObjectMethodProxy(self._indexes, 'filter')
        self.values = DictObjectMethodProxy(self._indexes, 'values')
    
    @property
    def backend(self):
        return self.schema._meta.get_backend()
    
    @property
    def collection(self):
        return self.schema._meta.collection
    
    def enable_index(self, index_cls_name, index_name, params):
        #TODO lazy load
        index_cls = self.backend.get_indexer(index_cls_name)
        indexer = index_cls(self.schema, index_name, params)
        self._indexes[index_name] = indexer
    
    def get_indexes(self):
        return self._indexes

COLLECTION_INDEXES = dict()

class Manager(object):
    def contribute_to_class(self, cls, name):
        new = copy(self)
        new.schema = cls
        setattr(cls, name, new)
    
    @property
    def backend(self):
        return self.schema._meta.get_backend()
    
    @property
    def collection(self):
        return self.schema._meta.collection
    
    @property
    def index_manager(self):
        if self.collection not in COLLECTION_INDEXES:
            COLLECTION_INDEXES[self.collection] = IndexManager(self.schema)
        return COLLECTION_INDEXES[self.collection]
    
    @property
    def filter(self):
        return self.index_manager.filter
    
    @property
    def values(self):
        return self.index_manager.values
    
    def all(self):
        return self.backend.all(self.schema, self.collection)
    
    def get(self, doc_id):
        data = self.backend.get(self.collection, doc_id)
        return self.schema.to_python(data)
    
    def enable_index(self, index_cls_name, index_name, params):
        return self.index_manager.enable_index(index_cls_name, index_name, params)
    
    def get_indexes(self):
        return self.index_manager.get_indexes()

'''
register_indexer(backend, "equals", index_cls)

Book.objects.enable_index("equals", "author_name", {'field':'author_name'})
Book.objects.enable_index("fulltext", "author_name__search", {'field':'author_name'})
Book.objects.filter.author_name__search('Twain')
Book.objects.values.author_name()

'''
