from copy import copy

from dockit.backends.queryindex import QueryIndex

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

class Manager(object):
    """
    The :class:`~dockit.schema.manager.Manager` class is assigned to the
    objects attribute of a document. The manager is used for retrieving
    documents.
    """
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
        """
        An accessor for the filters.
        """
        return self.all().filter(**kwargs)
    
    def index(self, *args):
        return self.all().index(*args)
    
    #def values(self):
    #    return self.index_manager.values
    
    def all(self):
        """
        Return all documents in the collection
        """
        return QueryIndex(self.schema)
    
    def count(self):
        return self.all().count()
    
    def get(self, **kwargs):
        """
        Return the document matching the arguments
        """
        return self.all().get(**kwargs)
    
    def filter_by_natural_key(self, hashval=None, **kwargs):
        if isinstance(hashval, dict):
            kwargs = hashval
            hashval = None
        if kwargs:
            if len(kwargs) == 1 and '@natural_key_hash' in kwargs:
                hashval = kwargs['@natural_key_hash']
            else:
                hashval = self.schema._get_natural_key_hash(kwargs)
        assert isinstance(hashval, basestring)
        queryset = self.filter(**{'@natural_key_hash':hashval})
        queryset._hashval = hashval #for debug purposes
        return queryset
    
    def get_by_natural_key(self, hashval=None, **kwargs):
        qs = self.filter_by_natural_key(hashval, **kwargs)
        real_hashval = qs._hashval
        try:
            return qs.get()
        except MultipleObjectsReturned, error:
            raise MultipleObjectsReturned('Duplicate natural keys found! Lookup parameters were %s. Natural key hash is: %s' % (hashval or kwargs, real_hashval))
        except ObjectDoesNotExist, error:
            raise ObjectDoesNotExist('Natural key not found! Lookup paramets were %s. Natural key hash is: %s' % (hashval or kwargs, real_hashval))

'''
register_indexer(backend, "equals", index_cls)

Book.objects.all().index('author_name__iexact').commit()
Book.objects.all().index('author_name__iexact').filter(author_name__iexact='Jane Doe')
#or
Book.objects.all().filter(author_name__iexact='Jane Doe')

Book.objects.all().index('author_name').values()
'''

