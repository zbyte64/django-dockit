
class BaseIndex(object):
    def __init__(self, document, name, params):
        super(BaseIndex, self).__init__()
        self.document = document
        self.name = name
        self.params = params
    
    @property
    def collection(self):
        return self.document._meta.collection
    
    def on_document_save(self, instance):
        pass
    
    def on_document_delete(self, instance):
        pass
    
    def filter(self):
        raise NotImplementedError
    
    def values(self):
        raise NotImplementedError

'''
register_indexer(backend, "equals", index_cls)

Book.objects.enable_index("equals", "author_name", {'field':'author_name'})
Book.objects.enable_index("fulltext", "author_name__search", {'field':'author_name'})
Book.objects.filter.author_name__search('Twain')
Book.objects.values.author_name()

Blog.objects.enable_index("date_parts", "publish_date", {'field':'publish_date'})
Blog.objects.filter.publish_date(year=2012)
Blog.objects.filter.publish_date(year=2012, month=11)
Blog.objects.filter.publish_date(year=2012, month=11, day=12)
Blog.objects.filter.publish_date(year__gt=2012) #feature for those who support it

Blog.objects.enable_index("category", "category", {'field':'category'})
Blog.objects.filter.category("shoes")
Blog.objects.filter.category("shoes/hiking")
Blog.objects.values.category() #gives a list of all the values for a given category
Blog.objects.values.category(parent="shoes") #gives a list of all the categories whose parent is shoes
'''
