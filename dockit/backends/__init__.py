from django.conf import settings

import threading

backend = None#threading.local()

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

def get_document_backends():
    backends = dict()
    config = getattr(settings, 'DOCKIT_BACKENDS')
    for key, value in config.iteritems():
        kwargs = dict(value)
        backend = dynamic_import(kwargs.pop('ENGINE'))
        backends[key] = lambda: backend(**kwargs)
    return backends

def get_document_backend():
    global backend
    if not backend:
        backends = get_document_backends()
        backend = backends['default']()
    return backend

