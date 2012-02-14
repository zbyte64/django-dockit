from django.conf import settings

backend = None

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

def get_document_backend():
    #TODO be thread safe
    global backend
    if not backend:
        backend_path = getattr(settings, 'DOCKIT_BACKEND', 'dockit.backends.djangodocument.backend.ModelDocumentStorage')
        backend = dynamic_import(backend_path)
        if isinstance(backend, type) or callable(backend):
            backend = backend()
    return backend

