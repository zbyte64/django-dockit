from django.forms.fields import ChoiceField, Field, EMPTY_VALUES
from django.forms.widgets import HiddenInput, SelectMultiple, MultipleHiddenInput
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode, smart_unicode

from django.utils import simplejson as json

from widgets import PrimitiveListWidget

class HiddenJSONField(Field):
    widget = HiddenInput
    
    def to_python(self, value):
        if value and isinstance(value, basestring):
            try:
                return json.loads(value)
            except ValueError:
                raise ValidationError("Invalid JSON")#TODO more descriptive error?
        return None

    def validate(self, value):
        return Field.validate(self, value)
    
    def prepare_value(self, value):
        if hasattr(value, 'to_primitive'):
            return json.dumps(type(value).to_primitive(value))
        return Field.prepare_value(self, value)

class HiddenSchemaField(HiddenJSONField):
    pass

class HiddenListField(HiddenJSONField):
    pass

class HiddenDictField(HiddenJSONField):
    pass

class PrimitiveListField(Field):
    '''
    Wraps around a subfield
    The widget receives the subfield and is responsible for rendering multiple iterations of the subfield and collecting of data
    '''
    widget = PrimitiveListWidget
    
    def __init__(self, subfield, *args, **kwargs):
        self.subfield = subfield
        widget = kwargs.get('widget', self.widget)
        if isinstance(widget, type):
            widget = widget(subfield)
        kwargs['widget'] = widget
        super(PrimitiveListField, self).__init__(*args, **kwargs)
    
    def prepare_value(self, value):
        if value is None:
            return
        ret = list()
        for val in value:
            ret.append(self.subfield.prepare_value(val))
        return ret
    
    def bound_data(self, data, initial):
        ret = list()
        for data_item, initial_item in zip(data, initial):
            ret.append(self.subfield.bound_data(data_item, initial_item))
        return ret
    
    def clean(self, data, initial=None):
        ret = list()
        for i, data_item in enumerate(data):
            if initial and len(initial) >= i:
                initial_item = initial[i]
            else:
                initial_item = None
            ret.append(self.subfield.clean(data_item, initial_item))
        return ret

class SchemaChoiceIterator(object):
    def __init__(self, field):
        self.field = field
        self.queryset = field.queryset

    def __iter__(self):
        if self.field.empty_label is not None:
            yield (u"", self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    self.choice(obj) for obj in self.queryset.all()
                ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for obj in self.queryset.all():
                yield self.choice(obj)

    def __len__(self):
        return len(self.queryset)

    def choice(self, obj):
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj))

class SchemaChoiceField(ChoiceField):
    """A ChoiceField whose choices are a model QuerySet."""
    # This class is a subclass of ChoiceField for purity, but it doesn't
    # actually use any of ChoiceField's implementation.
    default_error_messages = {
        'invalid_choice': _(u'Select a valid choice. That choice is not one of'
                            u' the available choices.'),
    }

    def __init__(self, queryset, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None,
                 help_text=None, to_field_name=None, *args, **kwargs):
        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        self.cache_choices = cache_choices

        # Call Field instead of ChoiceField __init__() because we don't need
        # ChoiceField.__init__().
        Field.__init__(self, required, widget, label, initial, help_text,
                       *args, **kwargs)
        self.queryset = queryset
        self.choice_cache = None
        self.to_field_name = to_field_name

    def __deepcopy__(self, memo):
        result = super(ChoiceField, self).__deepcopy__(memo)
        # Need to force a new ModelChoiceIterator to be created, bug #11183
        result.queryset = result.queryset
        return result

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)

    # this method will be used to create object labels by the QuerySetIterator.
    # Override it to customize the label.
    def label_from_instance(self, obj):
        """
        This method is used to convert objects into strings; it's used to
        generate the labels for the choices presented by this object. Subclasses
        can override this method to customize the display of the choices.
        """
        return smart_unicode(obj)

    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices

        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. Note that we're instantiating a new ModelChoiceIterator *each*
        # time _get_choices() is called (and, thus, each time self.choices is
        # accessed) so that we can ensure the QuerySet has not been consumed. This
        # construct might look complicated but it allows for lazy evaluation of
        # the queryset.
        return SchemaChoiceIterator(self)

    choices = property(_get_choices, ChoiceField._set_choices)

    def prepare_value(self, value):
        if hasattr(value, '_meta'):
            if self.to_field_name:
                return value.serializable_value(self.to_field_name)
            else:
                return value.pk
        return super(SchemaChoiceField, self).prepare_value(value)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        try:
            value = self.queryset.get(pk=value)
        except (ValueError):#, self.queryset.model.DoesNotExist): #TODO catch the propr does not exist error
            raise ValidationError(self.error_messages['invalid_choice'])
        return value

    def validate(self, value):
        return Field.validate(self, value)

class SchemaMultipleChoiceField(SchemaChoiceField):
    widget = SelectMultiple
    hidden_widget = MultipleHiddenInput
    default_error_messages = {
        'list': _(u'Enter a list of values.'),
        'invalid_choice': _(u'Select a valid choice. %s is not one of the'
                            u' available choices.'),
        'invalid_pk_value': _(u'"%s" is not a valid value for a primary key.')
    }

    def __init__(self, queryset, cache_choices=False, required=True,
                 widget=None, label=None, initial=None,
                 help_text=None, *args, **kwargs):
        super(SchemaMultipleChoiceField, self).__init__(queryset, None,
            cache_choices, required, widget, label, initial, help_text,
            *args, **kwargs)

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple, set)):
            raise ValidationError(self.error_messages['list'])
        
        #TODO validate the pk values
        '''
        qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = set([force_unicode(getattr(o, key)) for o in qs])
        for val in value:
            if force_unicode(val) not in pks:
                raise ValidationError(self.error_messages['invalid_choice'] % val)
        '''
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return value

    def prepare_value(self, value):
        if hasattr(value, '__iter__'):
            return [super(SchemaMultipleChoiceField, self).prepare_value(v) for v in value]
        return super(SchemaMultipleChoiceField, self).prepare_value(value)

