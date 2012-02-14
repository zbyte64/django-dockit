from dockit.backends.indexer import BaseIndexer

from backend import MongoDocumentStorage

class ExactIndexer(BaseIndexer):
    def filter(self):
        dotpath = self.filter_operation.dotpath()
        value = self.filter_operation.value
        return {dotpath: value}
    
    def values(self):
        mdotpath = self.filter_operation.dotpath()
        value = self.filter_operation.value
        return {dotpath: value}

MongoDocumentStorage.register_indexer(ExactIndexer, 'exact')
