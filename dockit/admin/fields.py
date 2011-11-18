from django.forms import fields, widgets, ValidationError
from django.core.urlresolvers import reverse

from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils import simplejson as json

from dockit.forms.fields import HiddenJSONField

class DotPathWidget(widgets.Input):
    input_type = 'submit'
    
    def __init__(self, dotpath):
        self.dotpath = dotpath
        super(DotPathWidget, self).__init__()
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif not isinstance(value, basestring):
            value = json.dumps(value)
        path_parts = list()
        if self.dotpath:
            path_parts.append(self.dotpath)
        path_parts.append(name) #TODO consider this will break if there is a prefix!
        dotpath = '.'.join(path_parts)
        submit_attrs = self.build_attrs({}, type=self.input_type, name='_next_dotpath', value=dotpath)
        data_attrs = self.build_attrs(attrs, type='hidden', name=name, value=value)
        return mark_safe(u'<input%s /><input%s />' % (flatatt(submit_attrs), flatatt(data_attrs)))

class DotPathField(HiddenJSONField):
    widget = DotPathWidget
    
    def __init__(self, *args, **kwargs):
        self.dotpath = kwargs.pop('dotpath')
        if 'widget' not in kwargs:
            kwargs['widget'] = self.widget(dotpath=self.dotpath)
        super(DotPathField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if isinstance(value, basestring):
            if not value:
                return None
            return json.loads(value)
        return value

