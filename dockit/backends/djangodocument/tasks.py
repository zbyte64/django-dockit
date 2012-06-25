
class IndexTasks(object):
    def __init__(self, model):
        self.model = model
        self.manager = model.objects
    
    def get_query_index_params(self, query_index):
        return {'name': self.manager.get_query_index_name(query_index),
                'collection': query_index.collection,
                'query_hash': query_index._index_hash(),}
    
    def register_index(self, query_index):
        params = self.get_query_index_params(query_index)
        
        #TODO the rest should be done in a task
        self.manager.register_index(**params)
    
    def reindex(self, query_index):
        params = self.get_query_index_params(query_index)
        
        #TODO the rest should be done in a task
        self.manager.reindex(**params)
    
    def on_save(self, collection, doc_id, data):
        self.manager.on_save(collection, doc_id, data)
    
    def on_delete(self, collection, doc_id):
        self.manager.on_delete(collection, doc_id)

