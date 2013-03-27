#import is done inside function to prevent cyclic import with Celery


#core index functions; do not call directly
def register_index(name, collection, query_hash):
    from dockit.backends.djangodocument.models import RegisteredIndex
    RegisteredIndex.objects.register_index(name, collection, query_hash)

def destroy_index(name, collection, query_hash):
    from dockit.backends.djangodocument.models import RegisteredIndex
    RegisteredIndex.objects.remove_index(collection, query_hash)

def reindex(name, collection, query_hash):
    from dockit.backends.djangodocument.models import RegisteredIndex
    RegisteredIndex.objects.reindex(name, collection, query_hash)

def on_save(collection, doc_id, data):
    from dockit.backends.djangodocument.models import RegisteredIndex
    RegisteredIndex.objects.on_save(collection, doc_id, data)

def on_delete(collection, doc_id):
    from dockit.backends.djangodocument.models import RegisteredIndex
    RegisteredIndex.objects.on_delete(collection, doc_id)

class IndexTasks(object):
    def __init__(self):
        from dockit.backends.djangodocument.models import RegisteredIndex
        self.manager = RegisteredIndex.objects
    
    def get_query_index_params(self, query_index):
        return {'name': self.manager.get_query_index_name(query_index),
                'collection': query_index.collection,
                'query_hash': query_index._index_hash(),}
    
    def register_index(self, query_index):
        params = self.get_query_index_params(query_index)
        self.schedule_register_index(**params)
    
    def destroy_index(self, query_index):
        params = self.get_query_index_params(query_index)
        self.schedule_destroy_index(**params)
    
    def schedule_register_index(self, **params):
        register_index(**params)
    
    def schedule_destroy_index(self, **params):
        destroy_index(**params)
    
    def reindex(self, query_index):
        params = self.get_query_index_params(query_index)
        self.schedule_reindex(**params)
    
    def schedule_reindex(self, **params):
        reindex(**params)
    
    def on_save(self, collection, doc_id, data):
        self.schedule_on_save(collection, doc_id, data)
    
    def schedule_on_save(self, collection, doc_id, data):
        on_save(collection, doc_id, data)
    
    def on_delete(self, collection, doc_id):
        self.schedule_on_delete(collection, doc_id)
    
    def schedule_on_delete(self, collection, doc_id):
        on_delete(collection, doc_id)

class ZTaskIndexTasks(IndexTasks):
    def __init__(self):
        super(ZTaskIndexTasks, self).__init__()
        from django_ztask.decorators import task
        self._register_index = task()(register_index)
        self._destroy_index = task()(destroy_index)
        self._reindex = task()(reindex)
        self._on_save = task()(on_save)
        self._on_delete = task()(on_delete)
        
    def schedule_register_index(self, **params):
        self._register_index.async(**params)
    
    def schedule_destroy_index(self, **params):
        self._destroy_index.async(**params)
    
    def schedule_reindex(self, **params):
        self._reindex.async(**params)
    
    def schedule_on_save(self, collection, doc_id, data):
        self._on_save.async(collection, doc_id, data)
    
    def schedule_on_delete(self, collection, doc_id):
        self._on_delete.async(collection, doc_id)

class CeleryIndexTasks(IndexTasks):
    def __init__(self):
        super(CeleryIndexTasks, self).__init__()
        from celery.task import task
        self._register_index = task(register_index, ignore_result=True)
        self._destroy_index = task(destroy_index, ignore_result=True)
        self._reindex = task(reindex, ignore_result=True)
        self._on_save = task(on_save, ignore_result=True)
        self._on_delete = task(on_delete, ignore_result=True)
        
    def schedule_register_index(self, **params):
        self._register_index.delay(**params)
    
    def schedule_destroy_index(self, **params):
        self._destroy_index.delay(**params)
    
    def schedule_reindex(self, **params):
        self._reindex.delay(**params)
    
    def schedule_on_save(self, collection, doc_id, data):
        self._on_save.delay(collection, doc_id, data)
    
    def schedule_on_delete(self, collection, doc_id):
        self._on_delete.delay(collection, doc_id)
