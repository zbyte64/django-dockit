class BaseDocumentQuery(object):
    """
    Implemented by the backend to execute a certain index
    """
    def __init__(self, query_index):
        self.query_index = query_index
    
    @property
    def document(self):
        return self.query_index.document
    
    @property
    def backend(self):
        return self.document._meta.get_index_backend_for_read(self.query_index)
    
    def _get_indexer_for_operation(self, document, op):
        return self.backend._get_indexer_for_operation(document, op)
    
    def __len__(self):
        raise NotImplementedError
    
    def count(self):
        return self.__len__()
    
    def exists(self):
        return bool(self.__len__())
    
    def delete(self):
        raise NotImplementedError
    
    def get(self, **kwargs):
        filter_operations = self.query_index._parse_kwargs(kwargs)
        return self.get_from_filter_operations(filter_operations)
    
    def get_from_filter_operations(self, filter_operations):
        raise NotImplementedError
    
    def values(self, *limit_to, **kwargs):
        raise NotImplementedError
    
    def __getitem__(self, val):
        raise NotImplementedError
    
    def __nonzero__(self):
        raise NotImplementedError

class QuerySet(object):
    '''
    Acts as a caching layer around an implemented `BaseDocumentQuery`
    TODO: implement actual caching
    '''
    def __init__(self, query):
        self.query = query
    
    @property
    def document(self):
        return self.query.document
    
    def __len__(self):
        #TODO cache
        return self.query.__len__()
    
    def count(self):
        return self.__len__()
    
    def delete(self):
        return self.query.delete()
    
    def values(self, *limit_to, **kwargs):
        #TODO cache
        return self.query.values(*limit_to, **kwargs)
    
    def get(self, **kwargs):
        #TODO cache
        return self.query.get(**kwargs)
    
    def exists(self):
        return self.query.exists()
    
    def __getitem__(self, val):
        #TODO cache
        return self.query.__getitem__(val)
    
    def __nonzero__(self):
        #TODO cache
        return self.query.__nonzero__()
    
    def __iter__(self):
        return iter(self.query)

