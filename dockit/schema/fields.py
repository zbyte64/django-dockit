from django.utils.encoding import smart_unicode, force_unicode, smart_str
from django.utils.text import capfirst
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import BLANK_CHOICE_DASH
from django import forms

from decimal import Decimal
import datetime

from serializer import PRIMITIVE_PROCESSOR
from dockit.forms.fields import HiddenJSONField, SchemaChoiceField

class NOT_PROVIDED:
    pass

class BaseField(object):
    meta_field = False
    form_field_class = forms.CharField
    form_widget_class = None
    
    def __init__(self, verbose_name=None, name=None, blank=False, null=False,
                 default=NOT_PROVIDED, editable=True,
                 serialize=True, choices=None, help_text='',
                 validators=[],
                 db_index=False, unique=False,
                #db_index=False,  db_column=None, primary_key=False, max_length=None
                #db_tablespace=None, auto_created=False, 
                #unique_for_date=None, unique_for_month=None, unique_for_year=None, 
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
        
        #TODO support the following:
        self.rel = None
        self.flatchoices = None
        self.unique = unique
    
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
    
    def formfield(self, **kwargs):
        "Returns a django.forms.Field instance for this database Field."
        form_class = kwargs.pop('form_class', self.form_field_class)
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
        return defaults
    
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
        if isinstance(self.coerce_function, type) and isinstance(val, self.coerce_function):
            return val
        return self.coerce_function(val)

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
    
    def to_python(self, val):
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

class BaseComplexField(BaseField):
    meta_field = True
    
    def formfield(self, form_class=HiddenJSONField, **kwargs):
        defaults = self.formfield_kwargs(**kwargs)
        return form_class(**defaults)

class ComplexDotNotationMixin(object):
    def dot_notation_to_value(self, notation, value):
        if notation is None:
            return value
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if isinstance(value, list):
            value = value[int(name)]
        elif isinstance(value, dict):
            value = value[name]
        else:
            value = getattr(value, name, None)
        return self.dot_notation_to_value(notation, value)
    
    def dot_notation_to_field(self, notation):
        return self
    
    def dot_notation_set_value(self, notation, value, parent):
        if notation is None:
            return super(SchemaField, self).dot_notation_set_value(notation, value, parent)
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if notation is None:
            #TODO value make primitive
            #value = PRIMITIVE_PROCESSOR.to_primitive(value)
            if hasattr(value, 'to_primitive'):
                value = value.to_primitive(value)
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
                parent.setdefault(name, dict())
                child = parent[name]
                if hasattr(child, 'dot_notation_set_value'):
                    return child.dot_notation_set_value(notation, value, parent)
                else:
                    return ComplexDotNotationMixin().dot_notation_set_value(notation, value, child)
            else:
                parent = getattr(parent, name)
                return self.schema._meta.fields[name].dot_notation_set_value(notation, value, parent)

class SchemaField(BaseComplexField):
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
        return self.schema._meta.fields[name].dot_notation_to_field(notation)
    
    def dot_notation_set_value(self, notation, value, parent):
        assert parent
        if notation is None:
            return super(SchemaField, self).dot_notation_set_value(notation, value, parent)
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if notation is None:
            setattr(parent, name, value)
        else:
            parent = getattr(parent, name)
            return self.schema._meta.fields[name].dot_notation_set_value(notation, value, parent)

class ListField(BaseComplexField):
    def __init__(self, schema=None, *args, **kwargs):
        self.schema = schema
        super(ListField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        if self.schema:
            ret = list()
            if val is None:
                return ret
            for item in val:
                ret.append(self.schema.to_primitive(item))
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_primitive(ret)
        return PRIMITIVE_PROCESSOR.to_primitive(val)
    
    def to_python(self, val):
        if self.schema:
            ret = list()
            if val is None:
                return ret
            for item in val:
                ret.append(self.schema.to_python(item))
            #run data through the primitive processor
            return PRIMITIVE_PROCESSOR.to_python(ret)
        return PRIMITIVE_PROCESSOR.to_primitive(val)
    
    def dot_notation_to_value(self, notation, value):
        if notation is None:
            return value
        if '.' in notation:
            index, notation = notation.split('.', 1)
        else:
            index, notation = notation, None
        if index == '*':
            raise NotImplementedError
        value = value[int(index)]
        return value.dot_notation_to_value(notation, value)
    
    def dot_notation_to_field(self, notation):
        if notation is None:
            return self;
        if '.' in notation:
            index, notation = notation.split('.', 1)
        else:
            index, notation = notation, None
        #print index, notation
        #index, notation = notation.split('.', 1)
        return self.schema.dot_notation_to_field(notation)
    
    def dot_notation_set_value(self, notation, value, parent):
        if notation is None:
            return super(SchemaField, self).dot_notation_set_value(notation, value, parent)
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if notation is None:
            index = int(name)
            if (len(parent) == index):
                parent.append(value)
            else:
                parent[index] = value
        else:
            child = parent[int(name)]
            if hasattr(child, 'dot_notation_set_value'):
                return child.dot_notation_set_value(notation, value, parent)
            else:
                return ComplexDotNotationMixin().dot_notation_set_value(notation, value, child)

class DictField(BaseComplexField):
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
    
    def dot_notation_set_value(self, notation, value, parent):
        if notation is None:
            return super(SchemaField, self).dot_notation_set_value(notation, value, parent)
        if '.' in notation:
            name, notation = notation.split('.', 1)
        else:
            name, notation = notation, None
        if notation is None:
            parent[name] = value
        else:
            parent.setdefault(name, dict())
            child = parent[name]
            if hasattr(child, 'dot_notation_set_value'):
                return child.dot_notation_set_value(notation, value, parent)
            else:
                return ComplexDotNotationMixin().dot_notation_set_value(notation, value, child)

class ReferenceField(ComplexDotNotationMixin, BaseField):
    form_field_class = SchemaChoiceField
    
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
    
    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.document.objects)
        return kwargs

class ModelReferenceField(BaseField):
    form_field_class = forms.ModelChoiceField
    
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(ModelReferenceField, self).__init__(*args, **kwargs)
    
    def to_primitive(self, val):
        if val is None:
            return None
        return val.pk
    
    def to_python(self, val):
        if val is None:
            return None
        return self.model.objects.get(pk=val)
    
    def formfield_kwargs(self, **kwargs):
        kwargs = BaseField.formfield_kwargs(self, **kwargs)
        kwargs.setdefault('queryset', self.model.objects)
        return kwargs

