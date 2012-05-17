import threading

DOCUMENT_BACKEND_CONNECTIONS = {}
THREADED_DOCUMENT_BACKEND_CONNECTIONS = threading.local()

INDEX_BACKEND_CONNECTIONS = {}
THREADED_INDEX_BACKEND_CONNECTIONS = threading.local()

class BaseStorage(object):
    thread_safe = False
    _connections = None
    _threaded_connections = None
    
    @classmethod
    def get_constructor(cls, key, options):
        if cls.thread_safe:
            def constructor():
                if key not in cls._connections:
                    cls._connections[key] = cls(**options)
                return cls._connections[key]
            return constructor
        else:
            def constructor():
                if not getattr(cls._threaded_connections, key, None):
                    setattr(cls._threaded_connections, key, cls(**options))
                return getattr(cls._threaded_connections, key)
            return constructor

class BaseIndexStorage(BaseStorage):
    _connections = INDEX_BACKEND_CONNECTIONS
    _threaded_connections = THREADED_INDEX_BACKEND_CONNECTIONS
    
    _indexers = dict()
    
    @classmethod
    def register_indexer(cls, index_cls, *names):
        for name in names:
            cls._indexers[name] = index_cls
    
    @classmethod
    def get_indexer(cls, name):
        return cls._indexers[name]
    
    def _get_indexer_for_operation(self, document, op):
        indexer = self.get_indexer(op.operation)
        return indexer(document, op)
    
    def register_index(self, query_index):
        raise NotImplementedError
    
    def get_query(self, query_index):
        raise NotImplementedError
    
    def register_document(self, document):
        pass
        #for key, field in document._meta.fields.iteritems():
        #    if getattr(field, 'db_index', False):
        #        document.objects.enable_index("equals", key, {'field_name':key})
    
    def on_save(self, doc_class, collection, doc_id, data):
        raise NotImplementedError
    
    def on_delete(self, doc_class, collection, doc_id):
        raise NotImplementedError

class BaseDocumentStorage(BaseStorage):
    _connections = DOCUMENT_BACKEND_CONNECTIONS
    _threaded_connections = THREADED_DOCUMENT_BACKEND_CONNECTIONS
    
    def get_query(self, query_index):
        raise NotImplementedError
    
    def register_document(self, document):
        pass
        #for key, field in document._meta.fields.iteritems():
        #    if getattr(field, 'db_index', False):
        #        document.objects.enable_index("equals", key, {'field_name':key})
    
    def save(self, doc_class, collection, data):
        raise NotImplementedError
    
    def get(self, doc_class, collection, doc_id):
        '''
        Returns the primitive data for that doc_id
        '''
        raise NotImplementedError
    
    def delete(self, doc_class, collection, doc_id):
        raise NotImplementedError
    
    def get_id(self, data):
        return data.get(self.get_id_field_name())
    
    def get_id_field_name(self):
        raise NotImplementedError

class BaseDocumentQuerySet(object):
    def __len__(self):
        raise NotImplementedError
    
    def count(self):
        return self.__len__()
    
    def delete(self):
        raise NotImplementedError
    
    def all(self):
        from copy import copy
        return copy(self)
    
    def get(self, doc_id):
        raise NotImplementedError
    
    def __getitem__(self, val):
        raise NotImplementedError
    
    def __nonzero__(self):
        raise NotImplementedError
    
    def __and__(self, other):
        raise NotImplementedError
    
    def __or__(self, order):
        raise NotImplementedError

