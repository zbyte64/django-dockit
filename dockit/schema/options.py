from dockit.backends import get_document_backend

import re

from django.conf import settings
from django.db.models.options import get_verbose_name
from django.utils.translation import activate, deactivate_all, get_language, string_concat
from django.utils.encoding import smart_str, force_unicode
from django.utils.datastructures import SortedDict, MergeDict
from django.db.models import FieldDoesNotExist

from common import DotPathTraverser

class FieldsDict(MergeDict):
    def __init__(self, *dicts):
        self.fields = SortedDict()
        dicts = [self.fields] + list(dicts)
        super(FieldsDict, self).__init__(*dicts)
    
    def __setitem__(self, key, value):
        self.fields[key] = value
    
    def update(self, *args, **kwargs):
        return self.fields.update(*args, **kwargs)

class SchemaOptions(object):
    """ class based on django.db.models.options. We only keep
    useful bits."""
    
    abstract = True
    ordering = ['_id']
    
    DEFAULT_NAMES = ['verbose_name', 'db_table', 'ordering', 'schema_key',
                     'app_label', 'collection', 'virtual', 'proxy',
                     'typed_field', 'typed_key']
    
    def __init__(self, meta, app_label=None, parent_fields=[]):
        self.module_name, self.verbose_name = None, None
        self.verbose_name_plural = None
        self.object_name, self.app_label = None, app_label
        self.meta = meta
        self.fields = FieldsDict(*parent_fields)
        self.collection = None
        self.schema_key = None
        self.virtual = False #TODO all schemas are virtual
        self.proxy = False
        self._document = None
        self.typed_field = None
        self.typed_key = None
    
    def process_values(self, cls):
        cls._meta = self
        self._document = cls
        self.installed = re.sub('\.models$', '', cls.__module__) in settings.INSTALLED_APPS
        # First, construct the default values for these options.
        self.object_name = cls.__name__
        self.module_name = self.object_name.lower()
        self.verbose_name = get_verbose_name(self.object_name)
        self.collection = self.default_schema_key()
        self.schema_key = self.default_schema_key()

        # Next, apply any overridden values from 'class Meta'.
        if getattr(self, 'meta', None):
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in self.DEFAULT_NAMES + ['module_name']:
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
    
    def contribute_to_class(self, cls, name):
        #the following needs to happen after fields are populated
        if self.typed_field:
            if self.typed_key:
                if self.virtual:
                    raise TypeError("Virtual Schemas may not have a typed_key")
                #CONSIDER this will break if fields are registered after the meta, gennerally have the virtual create the field for you
                if self.typed_field not in self.fields:
                    raise TypeError("Non-virtual Schemas that specify a typed field and a typed key must have that typed field defined.")
                self.fields[self.typed_field].schemas[self.typed_key] = cls
                self.proxy = True
            else:
                #if not self.virtual:
                #    raise TypeError("Schemas that specify a typed_field and not a typed_key must be virtual.")
                if self.typed_field not in self.fields:
                    from fields import SchemaTypeField
                    self.polymorphic_schemas = SortedDict()
                    field = SchemaTypeField(self.polymorphic_schemas, editable=False)
                    field.contribute_to_class(cls, self.typed_field)
    
    def default_schema_key(self):
        return "%s.%s" % (smart_str(self.app_label), smart_str(self.module_name))
    
    def __str__(self):
        return self.collection

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
            if name == 'pk':
                return self.pk
            raise FieldDoesNotExist
        return self.fields[name]
    
    def get_field_by_name(self, name):
        """
        Returns the (field_object, model, direct, m2m), where field_object is
        the Field instance for the given name, model is the model containing
        this field (None for local fields), direct is True if the field exists
        on this model, and m2m is True for many-to-many relations. When
        'direct' is False, 'field_object' is the corresponding RelatedObject
        for this field (since the field doesn't have an instance associated
        with it).

        Uses a cache internally, so after the first access, this is very fast.
        """
        if name not in self.fields:
            raise FieldDoesNotExist
        return (self.fields[name], None, True, False)
    
    def get_ordered_objects(self):
        return []
    
    @property
    def pk(self):
        from fields import CharField
        return CharField(name='pk')
    
    def get_backend(self):
        return get_document_backend()
    
    def dot_notation_to_field(self, notation):
        traverser = DotPathTraverser(notation)
        traverser.resolve_for_schema(self._document)
        return traverser.current['field']
    
    def is_dynamic(self):
        return bool(self.typed_field)
    
    @property
    def local_fields(self):
        return self.fields.values()
    
    @property
    def many_to_many(self):
        return []

class DocumentOptions(SchemaOptions):
    abstract = False


