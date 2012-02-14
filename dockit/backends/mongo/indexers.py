from dockit.backends.indexer import BaseIndexer

from backend import MongoDocumentStorage

from pymongo.objectid import ObjectId

class ExactIndexer(BaseIndexer):
    def _get_key_value(self):
        dotpath = self.filter_operation.dotpath()
        value = self.filter_operation.value
        if dotpath in ('pk', '_pk', '_id') and value:
            value = ObjectId(value)
        if dotpath in ('pk', '_pk'):
            dotpath = '_id'
        return dotpath, value
    
    def filter(self):
        dotpath, value = self._get_key_value()
        return {dotpath: value}
    
    def values(self):
        dotpath, value = self._get_key_value()
        return {dotpath: value}

MongoDocumentStorage.register_indexer(ExactIndexer, 'exact')
