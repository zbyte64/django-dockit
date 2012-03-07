from django.forms.widgets import Widget, Media, HiddenInput
from django.utils.safestring import mark_safe
import django.utils.copycompat as copy

from django import forms
from django.forms.util import flatatt
from django.forms.formsets import formset_factory, ORDERING_FIELD_NAME, DELETION_FIELD_NAME

class PrimitiveListWidget(Widget):
    '''
    Wraps around a subfield
    The widget receives the subfield and is responsible for rendering multiple iterations of the subfield and collecting of data
    '''
    def __init__(self, subfield, attrs=None):
        self.subfield = subfield
        super(PrimitiveListWidget, self).__init__(attrs)
    
    def get_base_form_class(self):
        class BaseForm(forms.Form):
            value = self.subfield
        return BaseForm
    
    def get_formset_class(self, **kwargs):
        form_cls = self.get_base_form_class()
        kwargs.setdefault('can_order', True)
        kwargs.setdefault('can_delete', True)
        formset = formset_factory(form_cls, **kwargs)
        return formset

    def render(self, name, value, attrs=None):
        if not isinstance(value, list):
            value = self.decompress(value)
        
        final_attrs = self.build_attrs(attrs)
        
        formset_class = self.get_formset_class()
        initial=[{'value':val} for val in value]
        formset = formset_class(initial=initial, prefix=name)
        parts = ['<div class="list-row form-row"><table>%s</table></div>' % form.as_table() for form in formset]
        parts.append('<div id="%s-empty" class="list-row form-row empty-row"><table>%s</table></div>' % (name, formset.empty_form.as_table()))
        output = u'<div%s style="float: left;" class="primitivelistfield" data-prefix="%s">%s %s</div>' % (flatatt(final_attrs), name, formset.management_form, u''.join(parts))
        return mark_safe(output)
    
    def value_from_datadict(self, data, files, name):
        formset_class = self.get_formset_class()
        formset = formset_class(data=data, files=files, prefix=name)
        value = list()
        for form in formset.forms:
            val = dict()
            for key in ('value', ORDERING_FIELD_NAME, DELETION_FIELD_NAME):
                val[key] = form.fields[key].widget.value_from_datadict(data, files, form.add_prefix(key))
            value.append(val)
        return value
    
    def _has_changed(self, initial, data):
        if initial is None:
            initial = [u'' for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.decompress(initial)
        #for widget, initial, data in zip(self.widgets, initial, data):
        #    if widget._has_changed(initial, data):
        #        return True
        return True #CONSIDER where is my name?
        return False
    
    def decompress(self, value):
        """
        Returns a list of decompressed values for the given compressed value.
        The given value can be assumed to be valid, but not necessarily
        non-empty.
        """
        raise NotImplementedError('Subclasses must implement this method.')

    def _get_media(self):
        "Media for a multiwidget is the combination of all media of the subwidgets"
        media = Media()
        media += self.subfield.media
        definition = getattr(self, 'Media', None)
        if definition:
            media += Media(definition)
        return media
    media = property(_get_media)
    
    def __deepcopy__(self, memo):
        obj = super(PrimitiveListWidget, self).__deepcopy__(memo)
        obj.subfield = copy.deepcopy(self.subfield)
        return obj

