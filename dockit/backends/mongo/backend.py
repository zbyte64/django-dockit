from pymongo import Connection
from pymongo.objectid import ObjectId

from dockit.backends.base import BaseDocumentStorage, BaseDocumentQuerySet

from django.conf import settings

class DocumentQuery(BaseDocumentQuerySet):
    def __init__(self, collection, doc_class, params=None):
        self.collection = collection
        self.doc_class = doc_class
        self.params = params or list()
        super(DocumentQuery, self).__init__()
    
    def _build_params(self):
        if self.params:
            params = self.params
            if len(params) > 1:
                params = dict(params)
            return params
        return None
    
    @property
    def queryset(self):
        params = self._build_params()
        if params:
            try:
                return self.collection.find(params)
            except TypeError:
                #why is it pymongo wants tuples for some and dictionaries for others?
                return self.collection.find(dict(params))
        return self.collection.find()
    
    def wrap(self, entry):
        entry['_id'] = unicode(entry['_id'])
        return self.doc_class.to_python(entry)
    
    def delete(self):
        params = self._build_params()
        if params:
            return self.collection.remove(params)
        return self.collection.remove()
    
    def get(self, doc_id):
        cls = type(self)
        query = cls(self.collection, self.doc_class, [('_id', ObjectId(doc_id))])
        final_query = query & self
        try:
            return final_query[0]
        except IndexError:
            raise self.doc_class.DoesNotExist
    
    def __len__(self):
        return self.queryset.count()
    
    def __nonzero__(self):
        return bool(self.queryset)
    
    def _check_for_operation(self, other):
        if not isinstance(other, DocumentQuery):
            raise TypeError, "operation may only be done against other Document Queries"
        if self.doc_class != other.doc_class:
            raise TypeError, "operation may only be done with the same document type"
    
    def __getitem__(self, val):
        if isinstance(val, slice):
            results = list()
            #TODO i don't think mongo supports passing a slice
            for entry in self.queryset[val]:
                results.append(self.wrap(entry))
            return results
        else:
            return self.wrap(self.queryset[val])
    
    #TODO and & or operations
    def __and__(self, other):
        self._check_for_operation(other)
        cls = type(self)
        params = self.params + other.params
        return cls(self.collection, self.doc_class, params)

class MongoDocumentStorage(BaseDocumentStorage):

    def __init__(self, username=None, password=None, host=None, port=None, db=None):
        #TODO be proper about this
        self.connection = Connection(host or settings.MONGO_HOST, port or settings.MONGO_PORT)
        self.db = self.connection[db or settings.MONGO_DB]
        username = getattr(settings, 'MONGO_USER', None)
        password = getattr(settings, 'MONGO_PASSWORD', None)
        if username:
            self.db.authenticate(username, password)
    
    def save(self, doc_class, collection, data):
        id_field = self.get_id_field_name()
        if data.get(id_field, False) is None:
            del data[id_field]
        elif id_field in data:
            data[id_field] = ObjectId(data[id_field])
        self.db[collection].save(data, safe=True)
        data[id_field] = unicode(data[id_field])
    
    def get(self, doc_class, collection, doc_id):
        data = self.db[collection].find_one({'_id':ObjectId(doc_id)})
        if data is None:
            raise doc_class.DoesNotExist
        id_field = self.get_id_field_name()
        data[id_field] = unicode(data[id_field])
        return data
    
    def delete(self, doc_class, collection, doc_id):
        return self.db[collection].remove(ObjectId(doc_id), safe=True)
    
    def get_id_field_name(self):
        return '_id'
    
    def all(self, doc_class, collection):
        return DocumentQuery(self.db[collection], doc_class)

