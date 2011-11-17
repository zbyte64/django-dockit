from django.utils.encoding import smart_unicode, force_unicode, smart_str
from django.utils.text import capfirst
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import BLANK_CHOICE_DASH
from django import forms

from decimal import Decimal
import datetime

from serializer import PRIMITIVE_PROCESSOR

class NOT_PROVIDED:
    pass

class BaseField(object):
    meta_field = False
    
    def __init__(self, verbose_name=None, name=None, blank=False, null=False,
                 default=NOT_PROVIDED, editable=True,
                 serialize=True, choices=None, help_text='',
                 validators=[],
                 db_index=False,
                #db_index=False,  db_column=None, primary_key=False, max_length=None, unique=False, 
                #db_tablespace=None, auto_created=False, 
                #unique_for_date=None, unique_for_month=None, unique_for_year=None, 
                #rel=None,
                 error_messages=None):
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
    
    def to_python(self, val):
        return val
    
    def formfield(self, form_class=forms.CharField, **kwargs):
        "Returns a django.forms.Field instance for this database Field."
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name), 'help_text': self.help_text}
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()
        if self.choices:
            # Fields with choices get special treatment.
            include_blank = self.blank or not (self.has_default() or 'initial' in kwargs)
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = None
            form_class = forms.TypedChoiceField
            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that TypedChoiceField will understand.
            for k in kwargs.keys():
                if k not in ('coerce', 'empty_value', 'choices', 'required',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)
    
    def dot_notation_to_value(self, notation, value):
        assert notation is None
        return value
    
    def dot_notation_to_field(self, notation):
        assert notation is None
        return self
    
    def dot_notation_set_value(self, notation, value, parent):
        assert notation is None
        setattr(parent, self.name, value)

class BaseTypedField(BaseField):
    coerce_function = None
    
    def to_primitive(self, val):
        return self.coerce_function(val)

class TextField(BaseTypedField):
    coerce_function = unicode

class IntegerField(BaseTypedField):
    coerce_function = int

class BigIntegerField(BaseTypedField):
    coerce_function = long

class BooleanField(BaseTypedField):
    coerce_function = bool

class DateField(BaseTypedField):
    coerce_function = datetime.date

class DateTimeField(BaseTypedField):
    coerce_function = datetime.datetime

class DecimalField(BaseField):
    def to_primitive(self, val):
        return str(val)
    
    def to_python(self, val):
        return Decimal(val)

class EmailField(TextField):
    pass #TODO validate

#TODO filefield? this will be passed off to the backend

class FloatField(BaseTypedField):
    coerce_function = float

#TODO imagefield

class IPAddressField(TextField):
    pass #TODO validate

class GenericIPAddressField(TextField):
    pass #TODO validate

#TODO NullBooleanField

class PositiveIntegerField(IntegerField):
    pass #TODO validate

#TODO PositiveSmallIntegerField

class SlugField(TextField):
    pass #TODO form field

#TODO SmallIntegerField

class TimeField(BaseTypedField):
    coerce_function = datetime.time

#TODO URLField
#TODO XMLField

class BaseComplexField(BaseField):
    meta_field = True
    
    def formfield(self, **kwargs):
        from dockit.forms.fields import HiddenJSONField
        kwargs.setdefault('form_class', HiddenJSONField)
        return BaseField.formfield(self, **kwargs)

class ComplexDotNotationMixin(object):
    def dot_notation_set_value(self, notation, value, parent):
        if notation is None:
            return super(SchemaField, self).dot_notation_set_value(notation, value, parent)
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if notation is None:
            if isinstance(parent, list):
                index = int(name)
                if (len(parent) == index):
                    parent.append(value)
                else:
                    parent[index] = value
            elif isinstance(parent, dict):
                parent[name] = value
            else:
                setattr(parent, name, value)
        else:
            if isinstance(parent, list):
                child = parent[int(name)]
                if hasattr(child, 'dot_notation_set_value'):
                    return child.dot_notation_set_value(notation, value, parent)
                else:
                    return ComplexDotNotationMixin().dot_notation_set_value(notation, value, child)
            elif isinstance(parent, dict):
                child = parent[name]
                if hasattr(child, 'dot_notation_set_value'):
                    return child.dot_notation_set_value(notation, value, parent)
                else:
                    return ComplexDotNotationMixin().dot_notation_set_value(notation, value, child)
            else:
                parent = getattr(parent, name)
                return self.schema._meta.fields[name].dot_notation_set_value(notation, value, parent)

class SchemaField(ComplexDotNotationMixin, BaseComplexField):
    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        super(SchemaField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        return self.schema.to_primitive(val)
    
    def to_python(self, val):
        return self.schema.to_python(val)
    
    def dot_notation_to_value(self, notation, value):
        if notation is None:
            return value
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        value = getattr(value, name, None)
        return self.schema._meta.fields[name].dot_notation_to_value(notation, value)
    
    def dot_notation_to_field(self, notation):
        if notation is None:
            return self
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        name, notation = notation.split('.', 1)
        return self.schema._meta.fields[name].dot_notation_to_field(notation)
    
class ListField(ComplexDotNotationMixin, BaseComplexField):
    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        super(ListField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        ret = list()
        if val is None:
            return ret
        for item in val:
            ret.append(self.schema.to_primitive(item))
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_primitive(ret)
        return ret
    
    def to_python(self, val):
        ret = list()
        if val is None:
            return ret
        for item in val:
            ret.append(self.schema.to_python(item))
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_python(ret)
        return ret
    
    def dot_notation_to_value(self, notation, value):
        if notation is None:
            return value
        if '.' in notation:
            index, notation = notation.split('.', 1)
        else:
            index, notation = notation, None
        if index == '*':
            pass #TODO support star
        value = value[index]
        return self.schema.dot_notation_to_value(notation, value)
    
    def dot_notation_to_field(self, notation):
        if notation is None:
            return self;
        if '.' in notation:
            index, notation = notation.split('.', 1)
        else:
            index, notation = notation, None
        index, notation = notation.split('.', 1)
        return self.schema.dot_notation_to_field(notation)

class DictField(ComplexDotNotationMixin, BaseComplexField):
    def __init__(self, key_schema=None, value_schema=None, **kwargs):
        self.key_schema = key_schema
        self.value_schema = value_schema
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
    
    def to_python(self, val):
        ret = dict()
        if val is None:
            return ret
        for key, value in val.iteritems():
            if self.value_schema:
                value = self.value_schema.to_python(value)
            if self.key_schema:
                key = self.key_schema.to_python(key)
            ret[key] = value
        #TODO run data through the primitive processor
        ret = PRIMITIVE_PROCESSOR.to_python(ret)
        return ret
    
    def dot_notation_to_value(self, notation, value):
        if notation is None:
            return value
        if '.' in notation:
            key, notation = notation.split('.', 1)
        else:
            key, notation = notation, None
        if key == '*':
            pass #TODO support star??
        value = value[key]
        return self.value_schema.dot_notation_to_value(notation, value)
    
    def dot_notation_to_field(self, notation):
        if notation is None:
            return self
        if '.' in notation:
            key, notation = notation.split('.', 1)
        else:
            key, notation = notation, None
        key, notation = notation.split('.', 1)
        return self.value_schema.dot_notation_to_field(notation)

class ReferenceField(ComplexDotNotationMixin, BaseField):
    def __init__(self, document, *args, **kwargs):
        assert hasattr(document, 'objects')
        assert hasattr(document, 'get_id')
        self.document = document
        super(ReferenceField, self).__init__(*args, **kwargs)
    
    @property
    def _meta(self):
        return self.document._meta
    
    def to_primitive(self, val):
        if isinstance(val, basestring): #CONSIDER, should this happen?
            return val
        return val.get_id()
    
    def to_python(self, val):
        try:
            return self.document.objects.get(val)
        except ObjectDoesNotExist:
            return None

class ModelReferenceField(BaseField):
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(ModelReferenceField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        return val.pk
    
    def to_python(self, val):
        return self.model.objects.get(pk=val)
    
    #TODO formfield returns ModelChoieField

