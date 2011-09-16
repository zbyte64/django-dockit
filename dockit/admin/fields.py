from django.forms import fields, widgets, ValidationError
from django.core.urlresolvers import reverse

from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

from dockit.models import SchemaFragment

class LinkedJSONWidget(widgets.Input):
    class Media:
        js = ['js/admin/SchemaFragment.js']
    
    input_type = 'hidden'
    
    def __init__(self, uri, identifier):
        self.uri = uri
        self.identifier = identifier
        super(LinkedJSONWidget, self).__init__()
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        print final_attrs
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            #TODO create the fragment on request, requires us to know the path though
            fragment = SchemaFragment(identifier=self.identifier, data=type(value).to_primitive(value))
            fragment.save()
            final_attrs['value'] = force_unicode(fragment.get_id())
            #class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"
            return mark_safe(u'<input%s /><a href="%s?_popup=1&fragment=%s" onclick="return showFragmentPopup(this);" class="related-lookup" id="lookup_id_%s"/>Edit</a>' % (flatatt(final_attrs), reverse(self.uri), fragment.get_id(), name))
        #TODO how do we configure the display?
        else:
            return mark_safe(u'<input%s /><a href="%s?_popup=1" onclick="return showFragmentPopup(this);" class="related-lookup" id="lookup_id_%s"/>Add</a>' % (flatatt(final_attrs), reverse(self.uri), name))

class EmbededSchemaField(fields.CharField):
    widget = LinkedJSONWidget
    
    def __init__(self, *args, **kwargs):
        self.view = kwargs.pop('view')
        if 'widget' not in kwargs:
            kwargs['widget'] = self.widget(self.view.uri, identifier=self.view.get_identifier())
        super(EmbededSchemaField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value:
            return None
        storage = SchemaFragment.objects.get(value)
        if storage.identifier != self.view.get_identifier():
            raise ValidationError('This object does not match the field type.')
        return storage.data
        


