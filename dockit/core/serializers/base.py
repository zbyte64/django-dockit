"""
Module for abstract serializer/unserializer base classes.
"""

from StringIO import StringIO

from django.core.serializers.base import SerializationError, DeserializationError
from django.core.exceptions import ObjectDoesNotExist

class Serializer(object):
    """
    Abstract serializer base class.
    """

    # Indicates if the implemented serializer is only available for
    # internal Django use.
    internal_use_only = False

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = options.pop("stream", StringIO())
        self.use_natural_keys = options.pop("use_natural_keys", True)

        self.start_serialization()
        for obj in queryset:
            self.start_object(obj)
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()

    def start_serialization(self):
        """
        Called when serializing of the queryset starts.
        """
        raise NotImplementedError

    def end_serialization(self):
        """
        Called when serializing of the queryset ends.
        """
        pass

    def start_object(self, obj):
        """
        Called when serializing of an object starts.
        """
        raise NotImplementedError

    def end_object(self, obj):
        """
        Called when serializing of an object ends.
        """
        pass

    def getvalue(self):
        """
        Return the fully serialized queryset (or None if the output stream is
        not seekable).
        """
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()

class Deserializer(object):
    """
    Abstract base deserializer class.
    """

    def __init__(self, stream_or_string, **options):
        """
        Init this serializer given a stream or a string
        """
        self.options = options
        if isinstance(stream_or_string, basestring):
            self.stream = StringIO(stream_or_string)
        else:
            self.stream = stream_or_string
        # hack to make sure that the models have all been loaded before
        # deserialization starts (otherwise subclass calls to get_model()
        # and friends might fail...)
        #models.get_apps()

    def __iter__(self):
        return self

    def next(self):
        """Iteration iterface -- return the next item in the stream"""
        raise NotImplementedError

class DeserializedObject(object):
    """
    A deserialized document.

    Basically a container for holding the pre-saved deserialized data.

    Call ``save()`` to save the object
    """

    def __init__(self, obj, natural_key=None):
        self.object = obj
        self.natural_key = natural_key

    def __repr__(self):
        return "<DeserializedObject: %s.%s(%s)>" % (
            self.object._meta.app_label, self.object._meta.object_name, self.natural_key)

    def save(self, enforce_natural_key=True):
        # Call save on the Model baseclass directly. This bypasses any
        # model-defined save. The save is also forced to be raw.
        # This ensures that the data that is deserialized is literally
        # what came from the file, not post-processed by pre_save/save
        # methods.
        
        #if an object with the natural key already exists, replace it while preserving the data store id
        if enforce_natural_key:
            manager = type(self.object).objects
            previous_objects = manager.filter_by_natural_key(self.natural_key)
            if previous_objects.count() > 1:
                for obj in list(previous_objects)[1:]:
                    obj.delete() #!!!!!! TODO emit a warning or something...
            if previous_objects:
                #Does this work?
                previous_obj = previous_objects[0]
                pk_field = previous_obj._meta.get_id_field_name()
                pk_value = previous_obj._primitive_data[pk_field]
                print 'Replacing id: %s\t natural key: %s' % (pk_value, self.natural_key)
                self.object._primitive_data[pk_field] = pk_value
        self.object.save()
        return self.object


