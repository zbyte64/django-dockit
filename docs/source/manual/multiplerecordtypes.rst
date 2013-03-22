=====================
Multiple Record Types
=====================

Documents and Schemas maybe subclassed to provide polymorphic functionality. For this to work the base class must define `typed_field` in its Meta class which specifies a field name to store the type of schema. The subclasses must define `typed_key` which is to be a unique string value identifying that sublcass.

Here is an example where a collection contains multiple record types::

    class ParentDocument(schema.Document):
        slug = schema.SlugField()
        
        class Meta:
            typed_field = '_doctype'
    
    class Blog(ParentDocument):
        author = schema.CharField()
        body = schema.TextField()
        
        class Meta:
            typed_key = 'blog'
    
    class Video(ParentDocument):
        url = schema.CharField()
        thumbnail = schema.ImageField(blank=True, null=True)
        
        class Meta:
            typed_key = 'video'
    
    Blog(slug='blog-entry', author='John Smith', body='large description').save()
    Video(slug='a-video', url='http://videos/url').save()
    
    ParentDocument.objects.all() #an iterator containing a Blog and Video entry

Embedded schemas may also take advantage of this functionality as well::

    class Download(schema.Schema):
        class Meta:
            typed_field = '_dltype'
    
    class Bucket(schema.Document):
        slug = schema.SlugField()
        downloads = schema.ListField(schema.SchemaField(Download))
    
    class Image(Download):
        full_image = schema.ImageField()
        
        class Meta:
            typed_key = 'image'
    
    class Video(Download):
        url = schema.CharField()
        thumbnail = schema.ImageField(blank=True, null=True)
        
        class Meta:
            typed_key = 'video'
    
    bucket = Bucket(slug='my-bucket')
    bucket.downloads.append(Image(full_image=myfile))
    bucket.downloads.append(Video(url='http://videos/url'))
    bucket.save()

When we retrieve our bucket later we can expect the entries in downloads to be appropriately mapped to Image and Video. Outside applications may also add other Download record types and our Bucket class will be made aware of those types.
