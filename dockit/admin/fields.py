from django.forms import fields, widgets, ValidationError
from django.core.urlresolvers import reverse

from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

from dockit.models import SchemaFragment

class DotPathWidget(widgets.Input):
    input_type = 'submit'
    
    def __init__(self, dotpath):
        self.dotpath = dotpath
        super(DotPathWidget, self).__init__()
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class DotPathField(fields.CharField):
    widget = DotPathWidget
    
    def __init__(self, *args, **kwargs):
        self.view = kwargs.pop('view')
        if 'widget' not in kwargs:
            kwargs['widget'] = self.widget(self.view.uri, identifier=self.view.get_identifier())
        super(DotPathField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value:
            return None
        storage = SchemaFragment.objects.get(value)
        if storage.identifier != self.view.get_identifier():
            raise ValidationError('This object does not match the field type.')
        return storage.data
        


