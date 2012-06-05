from django.conf import settings

DOCUMENT_BACKENDS = None
DOCUMENT_ROUTER = None
INDEX_BACKENDS = None
INDEX_ROUTER = None

class CompositeDocumentRouter(object):
    def __init__(self, routers):
        self.routers = routers
    
    def get_storage_for_read(self, document):
        name = self.get_storage_name_for_read(document)
        return get_document_backends()[name]()
    
    def get_storage_for_write(self, document):
        name = self.get_storage_name_for_write(document)
        return get_document_backends()[name]()
    
    def get_storage_name_for_read(self, document):
        for router in self.routers:
            name = router.get_storage_for_read(document)
            if name is not None:
                return name
        return 'default'
    
    def get_storage_name_for_write(self, document):
        for router in self.routers:
            name = router.get_storage_for_write(document)
            if name is not None:
                return name
        return 'default'
    
    def register_document(self, document):
        collection = document._meta.collection
        
        backend = self.get_storage_for_read(document)
        backend.register_document(document)
        
        backend2 = self.get_storage_for_write(document)
        if backend != backend2:
            backend2.register_document(document)

class CompositeIndexRouter(object):
    def __init__(self, routers):
        self.routers = routers
        self.registered_querysets = dict()
    
    def get_effective_queryset(self, queryset):
        if queryset._index_hash() in self.registered_querysets:
            return {'queryset':queryset,
                    'score':0,
                    'inclusions':[],
                    'exclusions':[],}
        
        best_match = None
        query_inclusions = set(queryset.inclusions)
        query_exclusions = set(queryset.exclusions)
        query_indexes = set(queryset.indexes)
        
        collection = queryset.document._meta.collection
        
        for val in self.registered_querysets[collection].itervalues():
            val_indexes = set(val.indexes)
            val_inclusions = set(val.inclusions)
            val_exclusions = set(val.exclusions)
            
            #if not val_indexes.issuperset(query_indexes):
            #    #val doesn't have all the indexes that is requested
            #    continue
            #if not val_inclusions.
            score = 0
            
            inclusions = query_inclusions - val_inclusions #inclusions queryset has but val does not
            exclusions = query_exclusions - val_exclusions #exclusions queryset has but val does not
            
            disqualified = False
            
            for inclusion in inclusions:
                match = False
                for index in val_indexes:
                    if inclusion.key == index.key and inclusion.operation == index.operation:
                        match = True
                        break
                if match:
                    score += 1
                else:
                    disqualified = True
                    break
            if disqualified:
                continue
            
            for exclusion in exclusions:
                match = False
                for index in val_indexes:
                    if exclusion.key == index.key and exclusion.operation == index.operation:
                        match = True
                        break
                if match:
                    score += 1
                else:
                    disqualified = True
                    break
            if disqualified:
                continue
            
            if not best_match or score > best_match['score']:
                best_match = {'queryset':val,
                              'score':score,
                              'inclusions':list(inclusions),
                              'exclusions':list(exclusions),}
        assert best_match, 'Queryset not registered'
        return best_match
    
    def get_index_for_read(self, document, queryset):
        name = self.get_index_name_for_read(document, queryset)
        return get_index_backends()[name]()
    
    def get_index_for_write(self, document, queryset):
        name = self.get_index_name_for_write(document, queryset)
        return get_index_backends()[name]()
    
    def get_index_name_for_read(self, document, queryset):
        for router in self.routers:
            name = router.get_index_for_read(document, queryset)
            if name is not None:
                return name
        return get_document_router().get_storage_name_for_read(document)
    
    def get_index_name_for_write(self, document, queryset):
        for router in self.routers:
            name = router.get_index_for_write(document, queryset)
            if name is not None:
                return name
        return get_document_router().get_storage_name_for_write(document)
    
    def on_save(self, document, collection, object_id, data):
        querysets = self.registered_querysets.get(collection, {})
        for query in querysets.itervalues():
            backend = self.get_index_for_write(document, query)
            backend.on_save(document, collection, object_id, data)
    
    def on_delete(self, document, collection, object_id):
        querysets = self.registered_querysets.get(collection, {})
        for query in querysets.itervalues():
            backend = self.get_index_for_write(document, query)
            backend.on_delete(document, collection, object_id)
    
    def register_queryset(self, queryset):
        document = queryset.document
        collection = queryset.document._meta.collection
        key = queryset._index_hash()
        
        backend = document._meta.get_index_backend_for_write(queryset)
        backend.register_index(queryset)
        backend2 = document._meta.get_index_backend_for_read(queryset)
        if backend != backend2:
            backend2.register_index(queryset)
        
        self.registered_querysets.setdefault(collection, {})
        self.registered_querysets[collection][key] = queryset

DYNAMIC_IMPORT_CACHE = dict()

def dynamic_import(name):
    if not isinstance(name, str):
        return name
    if name in DYNAMIC_IMPORT_CACHE:
        return DYNAMIC_IMPORT_CACHE[name]
    original_name = name
    names = name.split('.')
    attr = names.pop()
    try:
        ret = __import__(name, globals(), locals(), [attr], -1)
    except ImportError:
        name = '.'.join(names)
        ret = __import__(name, globals(), locals(), [attr], -1)
    ret = getattr(ret, attr, ret)
    DYNAMIC_IMPORT_CACHE[original_name] = ret
    return ret

def get_document_router():
    global DOCUMENT_ROUTER
    if not DOCUMENT_ROUTER:
        router_paths = getattr(settings, 'DOCKIT_COLLECTION_ROUTERS', [])
        routers = list()
        for path in router_paths:
            routers.append(dynamic_import(path))
        DOCUMENT_ROUTER = CompositeDocumentRouter(routers)
    return DOCUMENT_ROUTER

def get_index_router():
    global INDEX_ROUTER
    if not INDEX_ROUTER:
        router_paths = getattr(settings, 'DOCKIT_INDEX_ROUTERS', [])
        routers = list()
        for path in router_paths:
            routers.append(dynamic_import(path))
        INDEX_ROUTER = CompositeIndexRouter(routers)
    return INDEX_ROUTER

def get_document_backends():
    global DOCUMENT_BACKENDS
    if not DOCUMENT_BACKENDS:
        DOCUMENT_BACKENDS = dict()
        config = getattr(settings, 'DOCKIT_BACKENDS')
        for key, value in config.iteritems():
            kwargs = dict(value)
            backend = dynamic_import(kwargs.pop('ENGINE'))
            DOCUMENT_BACKENDS[key] = backend.get_constructor(key, kwargs)
    return DOCUMENT_BACKENDS

def get_index_backends():
    global INDEX_BACKENDS
    if not INDEX_BACKENDS:
        INDEX_BACKENDS = dict()
        config = getattr(settings, 'DOCKIT_INDEX_BACKENDS', {})
        for key, value in config.iteritems():
            kwargs = dict(value)
            backend = dynamic_import(kwargs.pop('ENGINE'))
            INDEX_BACKENDS[key] = backend.get_constructor(key, kwargs)
    return INDEX_BACKENDS

def get_document_backend(document=None):
    if document is None:
        return get_document_backends()['default']()
    return get_document_router().get_storage_for_read(document)

def get_index_backend(document, queryset):
    return get_index_router().get_index_for_read(document, queryset)

