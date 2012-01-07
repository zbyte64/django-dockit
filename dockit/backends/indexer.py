
class BaseIndex(object):
    def enable_index(self, name, params):
        raise NotImplementedError
    
    def on_document_save(self, document):
        pass
    
    def on_document_delete(self, document):
        pass
    
    def filter(self):
        raise NotImplementedError
    
    def values(self):
        raise NotImplementedError

'''
register_indexer(backend, "equals", index_cls)

Book.enable_index("equals", "author_name", {'field':'author_name'})
Book.enable_index("fulltext", "author_name__search", {'field':'author_name'})
Book.objects.filter.author_name__search('Twain')
Book.objects.values.author_name()

Blog.enable_index("date_parts", "publish_date", {'field':'publish_date'})
Blog.objects.filter.publish_date(year=2012)
Blog.objects.filter.publish_date(year=2012, month=11)
Blog.objects.filter.publish_date(year=2012, month=11, day=12)
Blog.objects.filter.publish_date(year__gt=2012) #feature for those who support it

Blog.enable_index("category", "category", {'field':'category'})
Blog.objects.filter.category("shoes")
Blog.objects.filter.category("shoes/hiking")
Blog.objects.values.category() #gives a list of all the values for a given category
Blog.objects.values.category(parent="shoes") #gives a list of all the categories whose parent is shoes
'''
