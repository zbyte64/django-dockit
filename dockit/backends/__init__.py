from django.conf import settings

import threading

backends = None#threading.local()
router = None

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
    global router
    if not router:
        router_paths = getattr(settings, 'DOCKIT_COLLECTION_ROUTERS', [])
        routers = list()
        for path in router_paths:
            routers.append(dynamic_import(path))
        router = CompositeRouter(routers)
    return router

def get_document_backends():
    global backends
    if not backends:
        backends = dict()
        config = getattr(settings, 'DOCKIT_BACKENDS')
        for key, value in config.iteritems():
            kwargs = dict(value)
            backend = dynamic_import(kwargs.pop('ENGINE'))
            backends[key] = lambda: backend(**kwargs)
    return backends

def get_document_backend(document=None):
    if document is None:
        return get_document_backends()['default']()
    name = get_document_router().db(document)
    return get_document_backends()[name]()

class CompositeRouter(object):
    def __init__(self, routers):
        self.routers = routers
    
    def db(self, document):
        for router in self.routers:
            name = router.db(document)
            if name is not None:
                return name
        return 'default'

