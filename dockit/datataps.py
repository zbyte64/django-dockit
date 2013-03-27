'''
Example usage::

    from datatap.dataps import JSONStreamDataTap, ZipFileDataTap
    from dockit.datataps import DocumentDataTap
    
    #serialize documents
    outstream = JSONStreamDataTap(stream=sys.stdout)
    outstream.open('w'. for_datatap=ModelDataTap)
    source = DocumentDataTap(MyDocument, Blog.objects.filter(is_active=True))
    source.dump(outstream)
    
    instream = JSONStreamDataTap(stream=open('fixture.json', 'r'))
    DocumentDataTap.load(instream)
    
    #give me all active users to stdout
    DocumentDataTap.store(JSONStreamDataTap(stream=sys.stdout), User.objects.filter(is_active=True))
    
    #write Blog and BlogImages to a zipfile
    archive = ZipFileDataTap(filename='myblog.zip')
    archive.open('w', for_datatap=DocumentDataTap)
    #or do it in one line: archive = ZipFileDataTap(filename='myblog.zip', mode='w', for_datatap=DocumentDataTap)
    DocumentDataTap.store(archive, Blog, BlogImages)
    archive.close()
    
    archive = ZipFileDataTap(filename='myblog.zip', mode='r')
    DocumentDataTap.load(archive)

'''
from optparse import OptionParser

from django.core.files import File

from dockit import schema
from dockit.schema.loading import get_documents, get_document
from dockit.core.serializers.python import Serializer, Deserializer


from datatap.encoders import ObjectIteratorAdaptor
from datatap.loading import register_datatap
from datatap.datataps.base import DataTap, WriteStream


class DocumentWriteStream(WriteStream):
    def __init__(self, datatap, itemstream):
        super(DocumentWriteStream, self).__init__(datatap, Deserializer(itemstream))
    
    def process_item(self, item):
        #item is a deserialized object
        item.save()
        return item.object

class FileAwareSerializer(Serializer):
    def start_object(self, obj):
        #TODO set files in self._current
        return super(FileAwareSerializer, self).start_object(obj)

class DocumentIteratorAdaptor(ObjectIteratorAdaptor):
    def __init__(self, use_natural_keys=True, **kwargs):
        self.serializer = FileAwareSerializer()
        self.use_natural_keys = use_natural_keys
        super(DocumentIteratorAdaptor, self).__init__(**kwargs)
    
    def transform(self, obj):
        #TODO not thread safe
        self.serializer.serialize([obj], use_natural_keys=self.use_natural_keys)
        return self.serializer.objects.pop()

class DocumentDataTap(DataTap):
    '''
    Reads and writes from DocKit's Collections
    '''
    write_stream_class = DocumentWriteStream
    object_iterator_class = DocumentIteratorAdaptor
    
    def __init__(self, *collection_sources, **kwargs):
        '''
        :param collection_sources: Maybe a Document, a Document instance, a Document queryset or a list of Document instances.
        '''
        self.collection_sources = collection_sources or []
        super(DocumentDataTap, self).__init__(**kwargs)
    
    def get_raw_item_stream(self, filetap=None):
        '''
        Yields objects from the collection sources
        '''
        for source in self.collection_sources:
            try:
                is_doc = issubclass(source, schema.Document)
                is_instance = False
            except TypeError:
                is_doc = False
                is_instance = isinstance(source, schema.Document)
            
            if is_doc:
                queryset = source.objects.all().iterator()
            elif is_instance:
                queryset = [source]
            else:
                if hasattr(source, 'iterator'):
                    queryset = source.iterator()
                else:
                    queryset = source
            for item in queryset:
                yield item
    
    def write_item(self, item):
        '''
        Creates and returns a document instance
        '''
        result = Deserializer([item]).next()
        result.save()
        return result.object
    
    @classmethod
    def load_from_command_line(cls, arglist):
        '''
        usage::
        
            manage.py datatap Document [<app label>, ...] [<collection name>, ...]
        '''
        parser = OptionParser(option_list=cls.command_option_list)
        options, args = parser.parse_args(arglist)
        document_sources = list()
        for arg in args: #list of apps and collection names
            if '.' in arg:
                document_sources.append(get_document(*arg.rsplit(".", 1)))
            else:
                #get docs from appname
                document_sources.extend(get_documents(arg))
        return cls(*document_sources, **options.__dict__)

register_datatap('Document', DocumentDataTap)
