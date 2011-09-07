
class BaseDocumentStorage(object):
    def store(self, collection, document):
        raise NotImplementedError
        #document._data
    
    def fetch(self, collection, doc_id):
        raise NotImplementedError
    
    def define_index(self, collection, index):
        raise NotImplementedError
    
    def get_id(self, data):
        raise NotImplementedError
