import copy

from queryset import QuerySet

class QueryFilterOperation(object):
    def __init__(self, key, operation, value):
        self.key = key
        self.operation = operation
        if value is not None:
            from dockit.schema import Document
            from django.db.models import Model
            if isinstance(value, Model):
                value = value.pk
            if isinstance(value, Document):
                value = value.pk
        self.value = value
    
    def __hash__(self):
        assert self.key is not None
        assert self.operation is not None
        if self.value is None:
            return hash((self.key, self.operation))
        return hash((self.key, self.operation, self.value))
    
    def dotpath(self):
        parts = self.key.split('__')
        return '.'.join(parts)
    
    def __repr__(self):
        return '<QueryFilterOperation: key=%s, operation=%s, value=%s>' % (self.key, self.operation, self.value)
    
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return hash(self) == hash(other)

class QueryIndex(object):
    """
    The public API for constructing and calling indexes. 
    Acts similarly to Django's Queryset.
    """
    def __init__(self, document):
        self.name = None
        self.document = document
        self.inclusions = list()
        self.exclusions = list()
        self.indexes = list()
        
        self._queryset = None
    
    def _parse_key(self, key):
        #TODO detect and handle dotpath notation
        operation = 'exact'
        if '__' in key:
            key, operation = key.rsplit('__', 1)
        return key, operation
    
    def _parse_kwargs(self, kwargs):
        items = list()
        for key, value in kwargs.iteritems():
            #TODO proper parsing
            key, operation = self._parse_key(key)
            items.append(QueryFilterOperation(key=key, operation=operation, value=value))
        return items
    
    def _add_filter_parts(self, inclusions=[], exclusions=[], indexes=[]):
        new_index = type(self)(self.document)
        new_index.inclusions = self.inclusions + inclusions
        new_index.exclusions = self.exclusions + exclusions
        new_index.indexes = self.indexes + indexes
        return new_index
    
    def _clone(self):
        return self._add_filter_parts()
    
    def _pk_only(self):
        for inclusion in self.inclusions:
            if inclusion.key != 'pk' or inclusion.operation != 'exact':
                return False
        for exclusion in self.exclusions:
            if exclusion.key != 'pk' or exclusion.operation != 'exact':
                return False
        return True
    
    def _build_queryset(self):
        if (not self._pk_only() and (self.inclusions or self.exclusions or self.indexes)):
            backend = self.document._meta.get_index_backend_for_read(self)
        else:
            backend = self.document._meta.get_document_backend_for_read()
        query = backend.get_query(self)
        return QuerySet(query)
    
    @property
    def collection(self):
        return self.document._meta.collection
    
    @property
    def model(self):
        """
        For basic django compatibility with queryset message generation
        """
        return self.document
    
    @property
    def queryset(self):
        if self._queryset is None:
            self._queryset = self._build_queryset()
        return self._queryset
    
    def filter(self, **kwargs):
        inclusions = self._parse_kwargs(kwargs)
        return self._add_filter_parts(inclusions=inclusions)
    
    def exclude(self, **kwargs):
        exclusions = self._parse_kwargs(kwargs)
        return self._add_filter_parts(exclusions=exclusions)
    
    def index(self, *args):
        items = list()
        for arg in args:
            key, operation = self._parse_key(arg)
            items.append(QueryFilterOperation(key=key, operation=operation, value=None))
        return self._add_filter_parts(indexes=items)
    
    def commit(self):
        from dockit.schema.loading import register_indexes
        register_indexes(self.document._meta.app_label, self)
    
    def setname(self, name):
        self.name = name
    
    def _index_hash(self):
        parts = list()
        parts.append('inclusions:')
        parts.append(hash(tuple(self.inclusions)))
        parts.append('exclusions:')
        parts.append(hash(tuple(self.exclusions)))
        parts.append('indexes:')
        parts.append(hash(tuple(self.indexes)))
        return hash(tuple(parts))
    
    #proxy queryset methods
    def __len__(self):
        return self.queryset.__len__()
    
    def count(self):
        return self.__len__()
    
    def values(self, *limit_to, **kwargs):
        return self.queryset.values(*limit_to, **kwargs)
    
    def delete(self):
        #CONSIDER we are taking from an index a list of doc ids
        from dockit.backends import get_index_router
        #TODO index_router should detect if there are any userspace indexes, if not skip notifying indexes
        #TODO if there are userspace indexes, they should be notified in a task
        index_router = get_index_router()
        for doc in self.values('pk'):
            index_router.on_delete(self.document, self.collection, doc['pk'])
        return self.queryset.delete()
    
    def all(self):
        ret = copy.copy(self)
        ret._queryset = None
        return ret
    
    def get(self, **kwargs):
        inclusions = self._parse_kwargs(kwargs)
        queryset = self._add_filter_parts(inclusions=inclusions).queryset
        return queryset.get()
    
    def exists(self):
        return self.queryset.exists()
    
    def __getitem__(self, val):
        return self.queryset.__getitem__(val)
    
    def __nonzero__(self):
        return self.queryset.__nonzero__()
    
    def __values__(self):
        return self.queryset.values()
    
    def __iter__(self):
        return self.queryset.__iter__()

