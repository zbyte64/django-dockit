import os
import sys

from django.db.models.loading import AppCache
from django.utils.datastructures import SortedDict

from signals import document_registered

class DockitAppCache(AppCache):
    def register_documents(self, app_label, *documents):
        document_dict = self.app_documents.setdefault(app_label, SortedDict())
        for document in documents:
            doc_name = document._meta.object_name.lower()
            if doc_name in document_dict:
                # The same model may be imported via different paths (e.g.
                # appname.models and project.appname.models). We use the source
                # filename as a means to detect identity.
                fname1 = os.path.abspath(sys.modules[document.__module__].__file__)
                fname2 = os.path.abspath(sys.modules[document_dict[doc_name].__module__].__file__)
                # Since the filename extension could be .py the first time and
                # .pyc or .pyo the second time, ignore the extension when
                # comparing.
                if os.path.splitext(fname1)[0] == os.path.splitext(fname2)[0]:
                    continue
            document_dict[doc_name] = document
            self.documents[document._meta.collection] = document
        if self.app_cache_ready():
            self.register_documents_with_backend(documents)
            self.post_app_ready() #TODO find a better solution, like on_app_ready
        else:
            self.pending_documents.extend(documents)
    
    def register_documents_with_backend(self, documents):
        from dockit.backends import get_document_router
        router = get_document_router()
        
        for document in documents:
            router.register_document(document)
            document_registered.send_robust(sender=document._meta.collection, document=document)
    
    def get_document(self, app_label, document_name,
                  seed_cache=True, only_installed=True):
        """
        Returns the model matching the given app_label and case-insensitive
        model_name.

        Returns None if no model is found.
        """
        if seed_cache:
            self._populate()
        if self.pending_documents and self.app_cache_ready():
            self.post_app_ready()
        if only_installed and app_label not in self.app_labels:
            return None
        return self.app_documents.get(app_label, SortedDict()).get(document_name.lower())
    
    def get_documents(self):
        if self.pending_documents and self.app_cache_ready():
            self.post_app_ready()
        return self.documents.values()
    
    def get_base_document(self, key):
        if self.pending_documents and self.app_cache_ready():
            self.post_app_ready()
        return self.documents[key]
    
    def register_schemas(self, app_label, *schemas):
        schema_dict = self.app_schemas.setdefault(app_label, SortedDict())
        if self.app_cache_ready():
            self.register_schemas_with_backend(schemas)
    
    def register_schemas_with_backend(self, schemas):
        pass
    
    def register_indexes(self, app_label, *indexes):
        index_dict = self.app_indexes.setdefault(app_label, SortedDict())
        for index in indexes:
            index_name = index._index_hash()
            if index_name in index_dict:
                continue
            index_dict[index_name] = index
        if self.app_cache_ready():
            self.register_indexes_with_backend(indexes)
            self.post_app_ready() #TODO find a better solution, like on_app_ready
        else:
            self.pending_indexes.extend(indexes)
    
    def register_indexes_with_backend(self, indexes):
        from dockit.backends import get_index_router
        router = get_index_router()
        
        for index in indexes:
            router.register_queryset(index)
    
    def post_app_ready(self): #TODO this should be called when the connection is ready, not when the app is ready;
        self.write_lock.acquire()
        try:
            self.register_documents_with_backend(self.pending_documents)
            self.pending_documents = list()
            
            self.register_indexes_with_backend(self.pending_indexes)
            self.pending_indexes = list()
        finally:
            self.write_lock.release()

AppCache._AppCache__shared_state.update({'app_indexes': dict(),
                                         'app_documents': SortedDict(),
                                         'app_schemas': SortedDict(),
                                         'documents': dict(),
                                         'pending_documents': list(),
                                         'pending_indexes': list(),})

cache = DockitAppCache()

register_documents = cache.register_documents
register_schemas = cache.register_schemas
register_indexes = cache.register_indexes
get_base_document = cache.get_base_document
get_documents = cache.get_documents

