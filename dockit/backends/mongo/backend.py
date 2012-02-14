from pymongo import Connection
from pymongo.objectid import ObjectId

from dockit.backends.base import BaseDocumentStorage
from dockit.backends.queryset import BaseDocumentQuery

from django.conf import settings

class DocumentQuery(BaseDocumentQuery):
    def _build_params(self, include_indexes=False):
        params =  dict()
        for op in self.query_index.inclusions:
            indexer = self._get_indexer_for_operation(self.document, op)
            #i think this is horribly wrong
            params.update(indexer.filter())
        for op in self.query_index.exclusions:
            indexer = self._get_indexer_for_operation(self.document, op)
            params.update(indexer.filter())
        if include_indexes:
            for op in self.query_index.indexes:
                indexer = self._get_indexer_for_operation(self.document, op)
                params.update(indexer.filter())
        return params
    
    @property
    def collection(self):
        return self.document._meta.get_backend().get_collection(self.document._meta.collection)
    
    @property
    def queryset(self):
        params = self._build_params()
        if params:
            try:
                return self.collection.find(params)
            except TypeError:
                #why is it pymongo wants tuples for some and dictionaries for others?
                return self.collection.find(params.items())
        return self.collection.find()
    
    def wrap(self, entry):
        entry['_id'] = unicode(entry['_id'])
        return self.document.to_python(entry)
    
    def delete(self):
        params = self._build_params()
        if params:
            return self.collection.remove(params)
        return self.collection.remove()
    
    def get_from_filter_operations(self, filter_operations):
        params = self._build_params()
        for op in filter_operations:
            indexer = self._get_indexer_for_operation(self.document, op)
            params.update(indexer.filter())
        try:
            ret = self.collection.find_one(params)
        except TypeError:
            #why is it pymongo wants tuples for some and dictionaries for others?
            ret = self.collection.find_one(params.items())
        if ret is None:
            raise self.document.DoesNotExist
        return self.wrap(ret)
    
    def values(self):
        params = self._build_params(include_indexes=True)
        raise NotImplementedError
    
    def __len__(self):
        return self.queryset.count()
    
    def __nonzero__(self):
        return bool(self.queryset)
    
    def __getitem__(self, val):
        if isinstance(val, slice):
            results = list()
            #TODO i don't think mongo supports passing a slice
            for entry in self.queryset[val]:
                results.append(self.wrap(entry))
            return results
        else:
            return self.wrap(self.queryset[val])

class MongoDocumentStorage(BaseDocumentStorage):
    name = "mongodb"
    _indexers = dict() #TODO this should be automatic

    def __init__(self, username=None, password=None, host=None, port=None, db=None):
        #TODO be proper about this
        self.connection = Connection(host or settings.MONGO_HOST, port or settings.MONGO_PORT)
        self.db = self.connection[db or settings.MONGO_DB]
        username = getattr(settings, 'MONGO_USER', None)
        password = getattr(settings, 'MONGO_PASSWORD', None)
        if username:
            self.db.authenticate(username, password)
    
    def get_collection(self, collection):
        return self.db[collection]
    
    def save(self, doc_class, collection, data):
        id_field = self.get_id_field_name()
        if data.get(id_field, False) is None:
            del data[id_field]
        elif id_field in data:
            data[id_field] = ObjectId(data[id_field])
        self.get_collection(collection).save(data, safe=True)
        data[id_field] = unicode(data[id_field])
    
    def get(self, doc_class, collection, doc_id):
        data = self.get_collection(collection).find_one({'_id':ObjectId(doc_id)})
        if data is None:
            raise doc_class.DoesNotExist
        id_field = self.get_id_field_name()
        data[id_field] = unicode(data[id_field])
        return data
    
    def delete(self, doc_class, collection, doc_id):
        return self.get_collection(collection).remove(ObjectId(doc_id), safe=True)
    
    def get_id_field_name(self):
        return '_id'
    
    def register_index(self, query_index):
        query = self.get_query(query_index)
        params = query._build_params(include_indexes=True)
        for key in params.keys(): #TODO this is a hack
            params[key] = 1
        if params:
            collection = query_index.document._meta.collection
            try:
                self.get_collection(collection).ensure_index(params, background=True)
            except TypeError:
                self.get_collection(collection).ensure_index(params.items(), background=True)
    
    def get_query(self, query_index):
        return DocumentQuery(query_index)

