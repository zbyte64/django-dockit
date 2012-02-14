
class BaseDocumentStorage(object):
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

