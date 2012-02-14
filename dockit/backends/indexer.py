
class BaseIndexer(object):
    def __init__(self, document, filter_operation):
        self.document = document
        self.filter_operation = filter_operation
    
    @property
    def collection(self):
        return self.document._meta.collection
    
    def on_document_save(self, instance):
        pass
    
    def on_document_delete(self, instance):
        pass
    
    def filter(self):
        raise NotImplementedError
    
    def values(self):
        raise NotImplementedError

