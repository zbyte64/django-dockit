from django.utils.encoding import smart_unicode, force_unicode, smart_str
from django.utils.text import capfirst
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import BLANK_CHOICE_DASH
from django import forms

from decimal import Decimal
import datetime

from serializer import PRIMITIVE_PROCESSOR
from exceptions import DotPathNotFound
from common import get_schema, DotPathList, DotPathDict, UnSet
from dockit.forms.fields import HiddenSchemaField, HiddenListField, HiddenDictField, SchemaChoiceField

class NOT_PROVIDED:
    pass

class BaseField(object):
    form_field_class = forms.CharField
    form_widget_class = None
    
    creation_counter = 0
    auto_creation_counter = -1
    
    def __init__(self, verbose_name=None, name=None, blank=False, null=False,
                 default=NOT_PROVIDED, editable=True,
                 serialize=True, choices=None, help_text='',
                 validators=[],
                 db_index=False, unique=False,
                #db_index=False,  db_column=None, primary_key=False, max_length=None
                #db_tablespace=None, auto_created=False, 
                #unique_for_date=None, unique_for_month=None, unique_for_year=None, 
                 error_messages=None, auto_created=False):
        self.verbose_name = verbose_name
        self.name = name
        self.blank = blank
        self.null = null
        self.default = default
        self.editable = editable
        self.serialize = serialize,
        self.choices = choices
        self.help_text = help_text
        self.validators = validators
        self.db_index = db_index
        
        #TODO support the following:
        self.rel = None
        self.flatchoices = None
        self.unique = unique
        
        # Adjust the appropriate creation counter, and save our local copy.
        if auto_created:
            self.creation_counter = BaseField.auto_creation_counter
            BaseField.auto_creation_counter -= 1
        else:
            self.creation_counter = BaseField.creation_counter
            BaseField.creation_counter += 1
    
    def contribute_to_class(self, cls, name):
        self.name = name
        cls._meta.fields[name] = self
        setattr(cls, name, self)
    
    def has_default(self):
        "Returns a boolean of whether this field has a default value."
        return self.default is not NOT_PROVIDED

    def get_default(self):
        "Returns the default value for this field."
        if self.has_default():
            if callable(self.default):
                return self.default()
            return force_unicode(self.default, strings_only=True)
        if not self.blank or self.null:
            return None
        return ""
    
    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        """Returns choices with a default blank choices included, for use
        as SelectField choices for this field."""
        first_choice = include_blank and blank_choice or []
        if self.choices:
            return first_choice + list(self.choices)
        return first_choice
        #rel_model = self.rel.to
        #if hasattr(self.rel, 'get_related_field'):
        #    lst = [(getattr(x, self.rel.get_related_field().attname), smart_unicode(x)) for x in rel_model._default_manager.complex_filter(self.rel.limit_choices_to)]
        #else:
        #lst = [(x._get_pk_val(), smart_unicode(x)) for x in rel_model._default_manager.complex_filter(self.rel.limit_choices_to)]
        #return first_choice + lst

    def get_choices_default(self):
        return self.get_choices()
    
    def to_primitive(self, val):
        """
        Takes a python object and returns an object that is [json] serializable
        """
        return val
    
    def to_python(self, val, parent=None):
        return val
    
    def formfield(self, **kwargs):
        "Returns a django.forms.Field instance for this database Field."
        if self.choices:
            default = forms.ChoiceField
        else:
            default = self.form_field_class
        form_class = kwargs.pop('form_class', default)
        defaults = self.formfield_kwargs(**kwargs)
        return form_class(**defaults)
    
    def formfield_kwargs(self, **kwargs):
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text,
                    'widget':self.form_widget_class,}
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()
        
        for key, value in defaults.items():
            if value is None:
                del defaults[key]
        
        if self.choices:
            # Fields with choices get special treatment.
            include_blank = self.blank or not (self.has_default() or 'initial' in kwargs)
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            #defaults['coerce'] = self.to_python
            #if self.null:
            #    defaults['empty_value'] = None
            form_class = forms.TypedChoiceField
            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that TypedChoiceField will understand.
            for k in kwargs.keys():
                if k not in ('empty_value', 'choices', 'required',#'coerce',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]
        defaults.update(kwargs)
        return defaults
    
    def traverse_dot_path(self, traverser):
        traverser.end(field=self)
    
    def is_instance(self, value):
        return False
    
    def set_value(self, parent, attr, value):
        raise DotPathNotFound

class BaseTypedField(BaseField):
    coerce_function = None
    
    def to_primitive(self, val):
        if isinstance(self.coerce_function, type) and isinstance(val, self.coerce_function):
            return val
        if self.null and val is None:
            return val
        return self.coerce_function(val)
    
    def is_instance(self, val):
        if isinstance(self.coerce_function, type) and isinstance(val, self.coerce_function):
            return True
        if val is None:
            return True
        return False

class CharField(BaseTypedField):
    coerce_function = unicode

class TextField(BaseTypedField):
    coerce_function = unicode
    form_widget_class = forms.Textarea

class IntegerField(BaseTypedField):
    coerce_function = int
    form_field_class = forms.IntegerField

class BigIntegerField(BaseTypedField):
    coerce_function = long
    form_field_class = forms.IntegerField

class BooleanField(BaseTypedField):
    coerce_function = bool
    form_field_class = forms.BooleanField
    
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self.blank = True

class DateField(BaseTypedField):
    coerce_function = datetime.date
    form_field_class = forms.DateField

class DateTimeField(BaseTypedField):
    coerce_function = datetime.datetime
    form_field_class = forms.DateTimeField

class DecimalField(BaseField):
    form_field_class = forms.DecimalField
    
    def to_primitive(self, val):
        return str(val)
    
    def to_python(self, val, parent=None):
        return Decimal(val)

class EmailField(CharField):
    form_field_class = forms.EmailField
    pass #TODO validate

#TODO filefield? this will be passed off to the backend

class FloatField(BaseTypedField):
    coerce_function = float
    form_field_class = forms.FloatField

#TODO imagefield

class IPAddressField(CharField):
    form_field_class = forms.IPAddressField
    #TODO validate

#class GenericIPAddressField(TextField):
#    form_field_class = forms.GenericIPAddressField
#    #TODO validate

#TODO NullBooleanField

class PositiveIntegerField(IntegerField):
    form_field_class = forms.IntegerField
    #TODO validate

#TODO PositiveSmallIntegerField

class SlugField(CharField):
    form_field_class = forms.SlugField

#TODO SmallIntegerField

class TimeField(BaseTypedField):
    coerce_function = datetime.time
    form_field_class = forms.TimeField

#TODO URLField
#TODO XMLField

class SchemaTypeField(CharField):
    form_widget_class = forms.HiddenInput
    
    def __init__(self, schemas, *args, **kwargs):
        self.schemas = schemas
        super(SchemaTypeField, self).__init__(*args, **kwargs)
    
    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        """Returns choices with a default blank choices included, for use
        as SelectField choices for this field."""
        first_choice = include_blank and blank_choice or []
        if self.schemas:
            return first_choice + list(zip(self.schemas.keys(), self.schemas.keys()))
            #TODO allow schema to have a display label, perhaps verbose name?
        return first_choice

class SchemaField(BaseField):
    form_field_class = HiddenSchemaField
    
    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        super(SchemaField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        return self.schema.to_primitive(val)
    
    def to_python(self, val, parent=None):
        return self.schema.to_python(val, parent)
    
    def is_instance(self, val):
        if val is None:
            return True
        return isinstance(val, self.schema)
    
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            name = traverser.next_part
            value = traverser.current_value
            next_value = field = None
            
            if value:
                try:
                    next_value = value[name]
                except KeyError:
                    pass
            if name in self.schema._meta.fields:
                field = self.schema._meta.fields[name]
            
            traverser.next(field=field, value=next_value)
        else:
            traverser.end(field=self)
    
    def set_value(self, parent, attr, value):
        if value is UnSet:
            del parent[attr]
        else:
            parent[attr] = value

class GenericSchemaField(BaseField):
    def __init__(self, field_name='_type', **kwargs):
        self.type_field_name = field_name
        super(GenericSchemaField, self).__init__(**kwargs)
    
    def lookup_schema(self, key):
        return get_schema(key)
    
    def get_schema_type(self, val):
        return val._meta.schema_key
    
    def get_schema_choices(self):
        raise NotImplementedError
    
    def set_schema_type(self, val):
        val[self.type_field_name] = self.get_schema_type(val)
    
    def to_primitive(self, val):
        if hasattr(val, 'to_primitive'):
            self.set_schema_type(val)
            return val.to_primitive(val)
        return val
    
    def to_python(self, val, parent=None):
        if hasattr(val, 'to_python'):
            return val.to_python(val, parent)
        if not self.is_instance(val):
            key = val[self.type_field_name]
            schema_cls = self.lookup_schema(key)
            return schema_cls(_primitive_data=val)
        return val
    
    def is_instance(self, val):
        if val is None:
            return True
        from schema import Schema
        return isinstance(val, Schema)
    
    def traverse_dot_path(self, traverser):
        #CONSIDER if there is a value then return an exacto schema field
        if traverser.remaining_paths:
            name = traverser.next_part
            value = traverser.current_value
            next_value = field = None
            
            if value:
                try:
                    next_value = value[name]
                except KeyError:
                    pass
                
                if hasattr(value, '_meta') and hasattr(value._meta, 'fields') and name in value._meta.fields:
                    field = value._meta.fields[name]
            
            traverser.next(field=field, value=next_value)
        else:
            if traverser.current_value:
                traverser.end(field=SchemaField(schema=type(traverser.current_value)))
            else:
                traverser.end(field=self)
    
    def set_value(self, parent, attr, value):
        if value is UnSet:
            del parent[attr]
        else:
            parent[attr] = value

class TypedSchemaField(GenericSchemaField):
    def __init__(self, schemas, field_name='_type', **kwargs):
        self.schemas = schemas
        super(TypedSchemaField, self).__init__(field_name, **kwargs)
    
    def lookup_schema(self, key):
        return self.schemas[key]
    
    def get_schema_type(self, val):
        return val._meta.schema_key
    
    def get_schema_choices(self):
        return self.schemas.items()
    
    #TODO what about a widget?

#TODO need a more comprehensive form field and widget solution for these
class ListField(BaseField):
    form_field_class = HiddenListField
    
    def __init__(self, subfield=None, *args, **kwargs):
        self.subfield = subfield
        kwargs.setdefault('default', list)
        super(ListField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        if self.subfield:
            ret = list()
            if val is None:
                return ret
            for item in val:
                ret.append(self.subfield.to_primitive(item))
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_primitive(ret)
        return PRIMITIVE_PROCESSOR.to_primitive(val)
    
    def to_python(self, val, parent=None):
        if self.subfield:
            ret = DotPathList()
            if val is None:
                return ret
            #TODO pass in parent
            for item in val:
                if not self.subfield.is_instance(item):
                    item = self.subfield.to_python(item)
                ret.append(item)
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_python(ret)
        return PRIMITIVE_PROCESSOR.to_python(val)
    
    def is_instance(self, val):
        if val is None:
            return True
        if not isinstance(val, DotPathList):
            return False
        if self.subfield:
            for item in val:
                if not self.subfield.is_instance(item):
                    return False
        return True
    
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            new_value = None
            value = traverser.current_value
            name = traverser.next_part
            if value and name != '*':
                try:
                    new_value = value[int(name)]
                except ValueError:
                    raise DotPathNotFound(u"Invalid index given, must be an integer (%s)" % name)
                except IndexError:
                    pass
            traverser.next(field=self.subfield, value=new_value)
        else:
            traverser.end(field=self)
    
    def set_value(self, parent, attr, value):
        index = int(attr)
        if value is UnSet:
            parent.pop(index)
        else:
            if self.subfield and not self.subfield.is_instance(value):
                value = self.subfield.to_python(value)
            if index == len(parent):
                parent.append(value)
            else:
                parent[index] = value

class DictField(BaseField):
    form_field_class = HiddenDictField
    
    def __init__(self, key_subfield=None, value_subfield=None, **kwargs):
        self.key_subfield = key_subfield
        self.value_subfield = value_subfield
        super(DictField, self).__init__(**kwargs)
    
    def to_primitive(self, val):
        ret = dict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if hasattr(value, 'to_primitive'):
                value = type(value).to_primitive(value)
            if hasattr(key, 'to_primitive'):
                key = type(key).to_primitive(key)
            ret[key] = value
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_primitive(ret)
        return ret
    
    def to_python(self, val, parent=None):
        ret = DotPathDict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if self.value_subfield:
                if not self.value_subfield.is_instance(value):
                    value = self.value_subfield.to_python(value)
            if self.key_subfield:
                if not self.key_subfield.is_instance(key):
                    key = self.key_subfield.to_python(key)
            ret[key] = value
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_python(ret)
        return ret
    
    def is_instance(self, val):
        if val is None:
            return True
        if not isinstance(val, DotPathDict):
            return False
        if self.value_subfield:
            for item in val.itervalues():
                if not self.value_subfield.is_instance(item):
                    return False
        if self.key_subfield:
            for item in val.iterkeys():
                if not self.key_subfield.is_instance(item):
                    return False
        return True
    
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            value = traverser.current_value
            name = traverser.next_part
            new_value = None
            if value and name != '*':
                try:
                    new_value = value[name]
                except KeyError:
                    pass
                if new_value and not hasattr(new_value, 'traverse_dot_path'):
                    from common import DotPathDict
                    new_value = DotPathDict(new_value)
            traverser.next(field=self.value_subfield, value=new_value)
        else:
            traverser.end(field=self)
    
    def set_value(self, parent, attr, value):
        if value is UnSet:
            del parent[attr]
        else:
            if self.value_subfield and not self.value_subfield.is_instance(value):
                value = self.value_subfield.to_python(value)
            parent[attr] = value

class ReferenceField(BaseField):
    form_field_class = SchemaChoiceField
    
    def __init__(self, document, *args, **kwargs):
        assert hasattr(document, 'objects')
        assert hasattr(document, 'get_id')
        self.document = document
        super(ReferenceField, self).__init__(*args, **kwargs)
    
    @property
    def _meta(self):
        return self.document._meta
    
    def is_instance(self, val):
        if val is None:
            return True
        return isinstance(val, self.document)
    
    def to_primitive(self, val):
        if isinstance(val, basestring): #CONSIDER, should this happen?
            return val
        return val.get_id()
    
    def to_python(self, val, parent=None):
        try:
            return self.document.objects.get(val)
        except ObjectDoesNotExist:
            return None
    
    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.document.objects)
        return kwargs
    
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            name = traverser.next_part
            value = traverser.current_value
            next_value = field = None
            
            if value:
                try:
                    next_value = value[name]
                except KeyError:
                    pass
            if name in self.document._meta.fields:
                field = self.document._meta.fields[name]
            
            traverser.next(field=field, value=next_value)
        else:
            traverser.end(field=self)
    
    def set_value(self, parent, attr, value):
        parent[attr] = value

class ModelReferenceField(BaseField):
    form_field_class = forms.ModelChoiceField
    
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(ModelReferenceField, self).__init__(*args, **kwargs)
    
    def is_instance(self, val):
        if val is None:
            return True
        return isinstance(val, self.model)
    
    def to_primitive(self, val):
        if val is None:
            return None
        return val.pk
    
    def to_python(self, val, parent=None):
        if val is None:
            return None
        return self.model.objects.get(pk=val)
    
    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.model.objects)
        return kwargs

