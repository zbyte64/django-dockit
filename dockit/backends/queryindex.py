import copy

from queryset import QuerySet



class QueryFilterOperation(object):
    def __init__(self, key, operation, value):
        self.key = key
        self.operation = operation
        from dockit.schema import Document
        from django.db.models import Model
        if isinstance(value, Model):
            value = value.pk
        if isinstance(value, Document):
            value = value.pk
        self.value = value
    
    def __hash__(self):
        return hash((self.key, self.operation, self.value))
    
    def dotpath(self):
        parts = self.key.split('__')
        return '.'.join(parts)

class QueryIndex(object):
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
    
    def _build_queryset(self):
        backend = self.document._meta.get_backend()
        query = backend.get_query(self)
        return QuerySet(query)
    
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
        backend = self.document._meta.get_backend()
        backend.register_index(self)
    
    def setname(self, name):
        self.name = name
    
    #proxy queryset methods
    def __len__(self):
        return self.queryset.__len__()
    
    def count(self):
        return self.__len__()
    
    def delete(self):
        return self.queryset.delete()
    
    def all(self):
        ret = copy.copy(self)
        ret._queryset = None
        return ret
    
    def get(self, **kwargs):
        return self.queryset.get(**kwargs)
    
    def __getitem__(self, val):
        return self.queryset.__getitem__(val)
    
    def __nonzero__(self):
        return self.queryset.__nonzero__()
    
    def __values__(self):
        return self.queryset.values()
    
    def __iter__(self):
        return self.queryset.__iter__()

