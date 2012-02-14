from copy import copy

from dockit.backends.queryindex import QueryIndex

class Manager(object):
    def contribute_to_class(self, cls, name):
        new = copy(self)
        new.schema = cls
        setattr(cls, name, new)
    
    @property
    def backend(self):
        return self.schema._meta.get_backend()
    
    @property
    def collection(self):
        return self.schema._meta.collection
    
    def filter(self, **kwargs):
        return self.all().filter(**kwargs)
    
    def index(self, *args):
        return self.all().index(*args)
    
    #def values(self):
    #    return self.index_manager.values
    
    def all(self):
        return QueryIndex(self.schema)
    
    def get(self, **kwargs):
        return self.all().get(**kwargs)

'''
register_indexer(backend, "equals", index_cls)

Book.objects.all().index('author_name__iexact').commit()
Book.objects.all().index('author_name__iexact').filter(author_name__iexact='Jane Doe')
#or
Book.objects.all().filter(author_name__iexact='Jane Doe')

Book.objects.all().index('author_name').values()
'''

