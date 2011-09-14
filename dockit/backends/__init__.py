backend = None

def get_document_backend():
    #TODO
    global backend
    if not backend:
        from djangodocument.backend import ModelDocumentStorage
        backend = ModelDocumentStorage()
    return backend

