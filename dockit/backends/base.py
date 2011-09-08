
class BaseDocumentStorage(object):
    def store(self, collection, data):
        raise NotImplementedError
    
    def fetch(self, collection, doc_id):
        raise NotImplementedError
    
    def define_index(self, collection, name, index):
        raise NotImplementedError
    
    def call_index(self, doc_class, collection, name, **kwargs):
        raise NotImplementedError
    
    def root_index(self, doc_class, collection):
        raise NotImplementedError
    
    def get_id(self, data):
        raise NotImplementedError

