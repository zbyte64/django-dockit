from dockit.backends.indexer import BaseIndexer

from backend import MongoDocumentStorage, DocumentQuery

class ExactIndexer(BaseIndexer):
    def __init__(self, *args, **kwargs):
        super(ExactIndexer, self).__init__(*args, **kwargs)
        self.dotpath = self.params.get('field', self.params.get('dotpath'))
        self.generate_index()
    
    def get_mongo_collection(self):
        backend = self.document._meta.get_backend()
        return backend.db[self.collection]
    
    def generate_index(self):
        mongo_collection = self.get_mongo_collection()
        mongo_collection.ensureIndex({self.dotpath:1})
    
    def filter(self, value):
        param = {self.dotpath: value}
        mongo_collection = self.get_mongo_collection()
        qs = mongo_collection.find(param)
        return DocumentQuery(qs, self.document)
    
    def values(self):
        mongo_collection = self.get_mongo_collection()
        return mongo_collection.distinct(self.dotpath)

MongoDocumentStorage.register_indexer("equals", ExactIndexer)

class DateIndexer(ExactIndexer):
    def filter(self, *args, **kwargs):
        mongo_collection = self.get_mongo_collection()
        if args:
            qs = mongo_collecion.find(args[0])
        #for key, value in kwargs.iteritems():
        #    qs = qs.filter(**filter_func('%s__%s' % (self.name, key), value))
            
        return DocumentQuery(qs, self.document)
    
    def values(self, *args, **kwargs):
        qs = DocumentStore.objects.filter(collection=self.collection)
        filter_func = self.index_functions['filter']
        if args:
            qs = qs.filter(**filter_func('%s__in' % self.name, args))
        for key, value in kwargs.iteritems():
            qs = qs.filter(**filter_func('%s__%s' % (self.name, key), value))
        return qs.values_list('dateindex__value', flat=True).distinct()

MongoDocumentStorage.register_indexer("date", DateIndexer)
