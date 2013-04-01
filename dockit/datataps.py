from optparse import OptionParser
from collections import deque

from django.core.files import File

from dockit import schema
from dockit.schema.loading import get_documents, get_document
from dockit.core.serializers.python import Serializer, Deserializer

from datatap.loading import register_datatap
from datatap.datataps.base import DataTap


class FileAwareSerializer(Serializer):
    def start_object(self, obj):
        #TODO set files in self._current
        return super(FileAwareSerializer, self).start_object(obj)

class DocumentDataTap(DataTap):
    '''
    Reads and writes from DocKit's Collections
    '''
    def __init__(self, instream=None, track_uncommitted=True, **kwargs):
        #this is so we can view objects and then easily commit
        if track_uncommitted:
            self.deserialized_objects = deque()
        else:
            self.deserialized_objects = None
        super(DocumentDataTap, self).__init__(instream, **kwargs)
    
    def get_domain(self):
        if self.instream is None: #no instream, I guess we write?
            return 'deserialized_document'
        if isinstance(self.instream, (list, tuple)):
            return 'primitive'
        if self.instream.domain == 'primitive':
            return 'deserialized_document'
    
    def get_instance_stream(self, instream):
        for source in instream:
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
    
    def get_primitive_stream(self, instream):
        '''
        Convert various model sources to primitive objects
        '''
        serializer = FileAwareSerializer()
        instances = self.get_instance_stream(instream)
        return serializer.serialize(instances)
    
    def get_deserialized_document_stream(self, instream):
        '''
        Convert primitive objects to deserialized document instances
        '''
        for deserialized_object in Deserializer(instream):
            if self.deserialized_objects is not None:
                self.deserialized_objects.append(deserialized_object)
            yield deserialized_object
    
    def get_document_stream(self, instream):
        '''
        Convert primitive objects to saved document instances
        '''
        for item in self.get_deserialized_document_stream(instream):
            item.save()
            yield item
    
    def commit(self):
        while self.deserialized_objects:
            instance = self.deserialized_objects.popleft()
            instance.save()
        self.deserialized_objects = None
        for instance in self:
            instance.save()
    
    @classmethod
    def load_from_command_line(cls, arglist, instream=None):
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
        return cls(instream=document_sources, **options.__dict__)

register_datatap('Document', DocumentDataTap)
