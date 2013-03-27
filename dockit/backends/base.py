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
    """
    The :class:`~dockit.backends.base.BaseIndexStorage` class provides an interface
    for implementing index storage backends.
    """
    
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
        """
        register the query index with this backend
        """
        raise NotImplementedError
    
    def destroy_index(self, query_index):
        """
        release the query index with this backend
        """
        raise NotImplementedError
    
    def get_query(self, query_index):
        """
        returns an implemented `BaseDocumentQuerySet` representing the query index
        """
        raise NotImplementedError
    
    def register_document(self, document):
        """
        is called for every document registered in the system
        """
        pass
    
    def on_save(self, doc_class, collection, doc_id, data):
        """
        is called for every document save
        """
        raise NotImplementedError
    
    def on_delete(self, doc_class, collection, doc_id):
        """
        is called for every document delete
        """
        raise NotImplementedError

class BaseDocumentStorage(BaseStorage):
    """
    The :class:`~dockit.backends.base.BaseDocumentStorage` class provides an interface
    for implementing document storage backends.
    """
    
    _connections = DOCUMENT_BACKEND_CONNECTIONS
    _threaded_connections = THREADED_DOCUMENT_BACKEND_CONNECTIONS
    
    def get_query(self, query_index):
        """
        return an implemented `BaseDocumentQuerySet` that contains all the documents
        """
        raise NotImplementedError
    
    def register_document(self, document):
        """
        is called for every document registered in the system
        """
        pass
    
    def save(self, doc_class, collection, data):
        """
        stores the given primitive data in the specified collection
        """
        raise NotImplementedError
    
    def get(self, doc_class, collection, doc_id):
        """
        returns the primitive data for the document belonging in the specified collection
        """
        raise NotImplementedError
    
    def delete(self, doc_class, collection, doc_id):
        """
        deletes the given document from the specified collection
        """
        raise NotImplementedError
    
    def get_id(self, data):
        """
        returns the id from the primitive data
        """
        return data.get(self.get_id_field_name())
    
    def get_id_field_name(self):
        """
        returns a string representing the primary key field name
        """
        raise NotImplementedError

class BaseDocumentQuerySet(object):
    """
    The :class:`~dockit.backends.base.BaseDocumentQuerySet` class provides an interface
    for implementing document querysets.
    """
    
    def __len__(self):
        """
        returns an integer representing the number of items in the queryset
        """
        raise NotImplementedError
    
    def count(self):
        """
        Alias of __len__
        """
        return self.__len__()
    
    def delete(self):
        """
        deletes all the documents in the given queryset
        """
        raise NotImplementedError
    
    def all(self):
        """
        Returns a copy of this queryset, minus any caching.
        """
        from copy import copy
        return copy(self)
    
    def get(self, doc_id):
        """
        returns the documents with the given id belonging to the queryset
        """
        raise NotImplementedError
    
    def __getitem__(self, val):
        """
        returns a document or a slice of documents
        """
        raise NotImplementedError
    
    def __nonzero__(self):
        """
        returns True if the queryset is not empty
        """
        raise NotImplementedError
    
    def __and__(self, other):
        raise NotImplementedError
    
    def __or__(self, order):
        raise NotImplementedError

