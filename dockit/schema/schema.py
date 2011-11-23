from dockit.backends import get_document_backend

import re
import sys

from django.conf import settings
from django.db.models.options import get_verbose_name
from django.utils.translation import activate, deactivate_all, get_language, string_concat
from django.utils.encoding import smart_str, force_unicode
from django.db.models import FieldDoesNotExist

from manager import Manager
from common import register_schema

class Options(object):
    """ class based on django.db.models.options. We only keep
    useful bits."""
    
    abstract = False
    ordering = ['_id']
    
    DEFAULT_NAMES = ('verbose_name', 'db_table', 'ordering',
                     'app_label', 'collection', 'virtual')
    
    def __init__(self, meta, app_label=None):
        self.module_name, self.verbose_name = None, None
        self.verbose_name_plural = None
        self.object_name, self.app_label = None, app_label
        self.meta = meta
        self.fields = dict() #TODO ordered dictionary
        self.collection = None
        self.virtual = False
    
    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.installed = re.sub('\.models$', '', cls.__module__) in settings.INSTALLED_APPS
        # First, construct the default values for these options.
        self.object_name = cls.__name__
        self.module_name = self.object_name.lower()
        self.verbose_name = get_verbose_name(self.object_name)
        self.collection = self.schema_key

        # Next, apply any overridden values from 'class Meta'.
        if getattr(self, 'meta', None):
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in self.DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))

            # verbose_name_plural is a special case because it uses a 's'
            # by default.
            setattr(self, 'verbose_name_plural', meta_attrs.pop('verbose_name_plural', string_concat(self.verbose_name, 's')))

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
            del self.meta
        else:
            self.verbose_name_plural = string_concat(self.verbose_name, 's')
    
    @property
    def schema_key(self):
        return "%s.%s" % (smart_str(self.app_label), smart_str(self.module_name))
    
    def __str__(self):
        return self.schema_key

    def verbose_name_raw(self):
        """
        There are a few places where the untranslated verbose name is needed
        (so that we get the same value regardless of currently active
        locale).
        """
        lang = get_language()
        deactivate_all()
        raw = force_unicode(self.verbose_name)
        activate(lang)
        return raw
    verbose_name_raw = property(verbose_name_raw)
    
    def get_field(self, name):
        if name not in self.fields:
            raise FieldDoesNotExist
        return self.fields[name]
    
    def get_field_by_name(self, name):
        if name not in self.fields:
            raise FieldDoesNotExist
        return self.fields[name]
    
    def get_ordered_objects(self):
        return []
    
    @property
    def pk(self):
        class DummyField(object):
            def __init__(self, **kwargs):
                for key, value in kwargs.iteritems():
                    setattr(self, key, value)
        return DummyField(attname='pk')

class SchemaBase(type):
    """
    Metaclass for all schemas.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(SchemaBase, cls).__new__
        
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        
        if getattr(meta, 'app_label', None) is None:
            document_module = sys.modules[new_class.__module__]
            app_label = document_module.__name__.split('.')[-2]
        else:
            app_label = getattr(meta, 'app_label')
        
        new_class.add_to_class('_meta', Options(meta, app_label=app_label))
        
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)
        
        if not new_class._meta.virtual:
            register_schema(new_class._meta.schema_key, new_class)
        
        return new_class
    
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

class Schema(object):
    __metaclass__ = SchemaBase
    
    def __init__(self, **kwargs):
        #super(Schema, self).__init-_()
        self._primitive_data = dict()
        self._python_data = dict()
        for key, value in kwargs.iteritems():
            #TODO check that key is a field or _data
            setattr(self, key, value)
        assert self._primitive_data is not None
        assert self._python_data is not None
    
    @classmethod
    def to_primitive(cls, val):
        #CONSIDER shouldn't val be a schema?
        if hasattr(val, '_primitive_data') and hasattr(val, '_python_data') and hasattr(val, '_meta'):
            #we've cached python values on access, we need to pump these back to the primitive dictionary
            for name, entry in val._python_data.iteritems():
                try:
                    val._primitive_data[name] = val._meta.fields[name].to_primitive(entry)
                except:
                    print name, val._meta.fields[name], entry
                    raise
            return val._primitive_data
        assert isinstance(val, (dict, list, None)), str(type(val))
        return val
    
    @classmethod
    def to_python(cls, val):
        if val is None:
            val = dict()
        return cls(_primitive_data=val)
    
    def __getattribute__(self, name):
        fields = object.__getattribute__(self, '_meta').fields
        if name in fields:
            python_data = object.__getattribute__(self, '_python_data')
            if name not in python_data:
                primitive_data = object.__getattribute__(self, '_primitive_data')
                python_data[name] = fields[name].to_python(primitive_data.get(name))
            return python_data[name]
        return object.__getattribute__(self, name)
    
    def __setattr__(self, name, val):
        if name in self._meta.fields:
            self._python_data[name] = val
            #field = self._fields[name]
            #store_val = field.to_primitive(val)
            #self._primtive_data[name] = store_val
        else:
            super(Schema, self).__setattr__(name, val)
    
    def dot_notation(self, notation):
        return self.dot_notation_to_value(notation, self)
    
    def dot_notation_set_value(self, notation, value, parent=None):
        #name = notation.split('.', 1)[0]
        original_notation = notation
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        
        if name not in self._meta.fields:
            from fields import ComplexDotNotationMixin
            return ComplexDotNotationMixin().dot_notation_set_value(original_notation, value, parent=self._primitive_data)
        else:
            if notation is None:
                setattr(self, name, value)
            else:
                self._meta.fields[name].dot_notation_set_value(notation, value, parent=getattr(self, name))
    
    def dot_notation_to_value(self, notation, value):
        if notation is None:
            return value
        original_notation = notation
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if name == '*':
            pass #TODO support star??
        if name not in self._meta.fields:
            from fields import ComplexDotNotationMixin
            return ComplexDotNotationMixin().dot_notation_to_value(original_notation, value._primitive_data)
        value = getattr(value, name, None)
        return self._meta.fields[name].dot_notation_to_value(notation, value)
    
    @classmethod
    def dot_notation_to_field(self, notation):
        if notation is None:
            return self
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if name not in self._meta.fields:
            from fields import ComplexDotNotationMixin
            return ComplexDotNotationMixin()
        return self._meta.fields[name].dot_notation_to_field(notation)

class DocumentBase(SchemaBase):
    def __new__(cls, name, bases, attrs):
        new_class = SchemaBase.__new__(cls, name, bases, attrs)
        if 'objects' not in attrs:
            objects = Manager()
            objects.contribute_to_class(new_class, 'objects')
        
        if not new_class._meta.virtual:
            backend = get_document_backend()
            backend.register_document(new_class)
        return new_class

class Document(Schema):
    __metaclass__ = DocumentBase
    
    def get_id(self):
        backend = get_document_backend()
        return backend.get_id(self._primitive_data)
    
    pk = property(get_id)
    
    def save(self):
        backend = get_document_backend()
        data = type(self).to_primitive(self)
        backend.save(self._meta.collection, data)
    
    def delete(self):
        backend = get_document_backend()
        backend.delete(self._meta.collection, self.get_id())
    
    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field_by_name(field_name)[0]
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)
    
    def __str__(self):
        if hasattr(self, '__unicode__'):
            return force_unicode(self).encode('utf-8')
        return '%s object' % self.__class__.__name__

def create_document(name, fields, module='dockit.models'):
    attrs = dict(fields)
    attrs['__module__'] = module
    class virtual_meta:
        virtual = True
    attrs['Meta'] = virtual_meta
    return DocumentBase.__new__(DocumentBase, name, (Document,), attrs)

