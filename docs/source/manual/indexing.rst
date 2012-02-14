Creating Indexes
================

Creating indexes in dockit is allot like constructing a django query except that no joins are currently allowed.
After constructing a query, calling commit() ensures that the database has an index covering the criteria you supplied.

Examples::

    #to create the index
    MyDocument.objects.filter(published=True).commit()
    #to use the index
    for doc in MyDocument.objects.filter(published=True):
        print doc
    
    #create an index for published documents that index the slug field
    MyDocument.objects.filter(published=True).index('slug').commit()
    #to use the index
    MyDocument.objects.filter(published=True).get(slug='this-slug')
    
    #index with a date
    MyDocument.objects.filter(published=True).index('publish_date')
    
    MyDocument.objects.filter(published=True).filter(publish_date__lte=datetime.datetime.now())

