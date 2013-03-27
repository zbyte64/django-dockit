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
    def __init__(self, *collection_sources, **kwargs):
        self.collection_sources = collection_sources or []
        super(DocumentDataTap, self).__init__(**kwargs)
    
    def get_object_iterator_class(self):
        return DocumentIteratorAdaptor
    
    def get_raw_item_stream(self, filetap=None):
        '''
        Yields objects from the collection sources
        '''
        for source in self.collection_sources:
            try:
                is_doc = issubclass(source, schema.Document)
            except TypeError:
                is_doc = False
            
            if is_doc:
                queryset = source.objects.all()
            else:
                queryset = source
            for item in queryset.iterator():
                yield item
    
    def write_stream(self, instream):
        a_stream = DocumentWriteStream(self, instream)
        self.open_writes.add(a_stream)
        return a_stream
    
    def write_item(self, item):
        '''
        Creates and returns a model instance
        '''
        result = Deserializer([item]).next()
        result.save()
        return result.object
    
    @classmethod
    def load_from_command_line(cls, arglist):
        parser = OptionParser(option_list=cls.command_option_list)
        options, args = parser.parse_args(arglist)
        document_sources = list()
        for arg in args: #list of apps and collection names
            if '.' in arg:
                document_sources.append(get_document(*arg.split(".", 1)))
            else:
                #get docs from appname
                document_sources.extend(get_documents(arg))
        return cls(*document_sources, **options.__dict__)

register_datatap('Document', DocumentDataTap)
