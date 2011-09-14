
class BaseDocumentStorage(object):
    def save(self, collection, data):
        raise NotImplementedError
    
    def get(self, collection, doc_id):
        raise NotImplementedError
    
    def generate_index(self, collection, field):
        raise NotImplementedError
    
    def define_index(self, collection, name, index):
        raise NotImplementedError
    
    def call_index(self, doc_class, collection, name, **kwargs):
        raise NotImplementedError
    
    def all(self, doc_class, collection):
        raise NotImplementedError
    
    def filter(self, doc_class, collection, params):
        raise NotImplementedError
    
    def get_id(self, data):
        raise NotImplementedError

