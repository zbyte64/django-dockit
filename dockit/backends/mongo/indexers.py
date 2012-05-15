from dockit.backends.indexer import BaseIndexer

from backend import MongoDocumentStorage

try:
    from bson.objectid import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId

class MongoIndexer(BaseIndexer):
    def _get_key_value(self):
        dotpath = self.filter_operation.dotpath()
        value = self.filter_operation.value
        if dotpath in ('pk', '_pk', '_id') and value:
            value = ObjectId(value)
        if dotpath in ('pk', '_pk'):
            dotpath = '_id'
        return dotpath, value

class ExactIndexer(MongoIndexer):
    def filter(self):
        dotpath, value = self._get_key_value()
        return {dotpath: value}
    
    def values(self):
        dotpath, value = self._get_key_value()
        return {dotpath: value}

MongoDocumentStorage.register_indexer(ExactIndexer, 'exact')

class OperationIndexer(MongoIndexer):
    operation = None
    
    def filter(self):
        dotpath, value = self._get_key_value()
        return {dotpath: { self.operation : value }}
    
    def values(self):
        dotpath, value = self._get_key_value()
        return {dotpath: { self.operation: value }}

class GTIndexer(OperationIndexer):
    operation = '$gt'

MongoDocumentStorage.register_indexer(GTIndexer, 'gt')

class LTIndexer(OperationIndexer):
    operation = '$lt'

MongoDocumentStorage.register_indexer(LTIndexer, 'lt')

class GTEIndexer(OperationIndexer):
    operation = '$gte'

MongoDocumentStorage.register_indexer(GTEIndexer, 'gte')

class LTEIndexer(OperationIndexer):
    operation = '$lte'

MongoDocumentStorage.register_indexer(LTEIndexer, 'lte')

class INIndexer(OperationIndexer):
    operation = '$in'

MongoDocumentStorage.register_indexer(LTEIndexer, 'in')

