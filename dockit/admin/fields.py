from django.forms import widgets

from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils import simplejson as json

from dockit.forms.fields import HiddenJSONField

from urllib import urlencode

class DotPathWidget(widgets.Input):
    input_type = 'submit'
    
    def __init__(self, dotpath=None):
        self.dotpath = dotpath
        super(DotPathWidget, self).__init__()
    
    def render_button(self, dotpath, edit=False):
        if edit:
            label = 'edit'
        else:
            label = 'add'
        data = {'next_dotpath':dotpath}
        name = '[fragment]%s' % urlencode(data)
        submit_attrs = self.build_attrs({}, type=self.input_type, name=name, value=label)
        return mark_safe(u'<input%s />' % flatatt(submit_attrs))
    
    def prep_value(self, value):
        if isinstance(value, list):
            new_values = list()
            for item in value:
                if hasattr(item, 'to_primitive'):
                    item = item.to_primitive(item)
                new_values.append(item)
            value = new_values
        if hasattr(value, 'to_primitive'):
            value = value.to_primitive(value)
        if value is None:
            return ''
        elif not isinstance(value, basestring): 
            return json.dumps(value)
        return value
    
    def get_label(self, dothpath, value=None):
        if value:
            return escape(force_unicode(value))
        return ''
    
    def render(self, name, value, attrs=None):
        path_parts = list()
        if self.dotpath:
            path_parts.append(self.dotpath)
        path_parts.append(name) #TODO consider this will break if there is a prefix!
        dotpath = '.'.join(path_parts)
        json_value = self.prep_value(value)
        
        data_attrs = self.build_attrs(attrs, type='hidden', name=name, value=json_value)
        data_html = mark_safe(u'<input%s />' % flatatt(data_attrs))
        
        if isinstance(value, list):
            rows = list()
            index = -1
            for index, item in enumerate(value):
                item_dotpath = '%s.%s' % (dotpath, index)
                butn_html = self.render_button(item_dotpath, edit=True)
                rows.append('<td>%s</td><td>%s</td>' % (self.get_label(item_dotpath, item), butn_html))
            item_dotpath = '%s.%s' % (dotpath, index+1)
            butn_html = self.render_button(item_dotpath)
            rows.append('<td>%s</td><td>%s</td>' % (self.get_label(item_dotpath), butn_html))
            return mark_safe('%s<table><tr>%s</tr></table>' % (data_html, '</tr><tr>'.join(rows)))
        else:
            butn_html = self.render_button(dotpath, edit=bool(value))
            desc_html = self.get_label(dotpath, value)
            return mark_safe(''.join((data_html, desc_html, butn_html)))

class DotPathField(HiddenJSONField):
    widget = DotPathWidget
    
    def __init__(self, *args, **kwargs):
        self.dotpath = kwargs.pop('dotpath')
        #if 'widget' not in kwargs or self.widget == kwargs['widget']:
        #    kwargs['widget'] = self.widget(dotpath=self.dotpath)
        super(DotPathField, self).__init__(*args, **kwargs)
        self.widget.dotpath = self.dotpath
    
    def prepare_value(self, value):
        return value


class TypedSchemaFieldWidget(DotPathWidget):
    input_type = 'submit'
    
    def __init__(self, dotpath=None, schema_property=None):
        self.dotpath = dotpath
        self.schema_property = schema_property
        super(DotPathWidget, self).__init__()
    
    def render_type_dropdown(self, dotpath):
        options = list()
        for val, label in self.schema_property.get_schema_choices():
            options.append(u'<option value="%s">%s</option>' % (escape(force_unicode(val)), escape(force_unicode(label))))
        data = {'next_dotpath':dotpath,
                'name':self.schema_property.type_field_name,}
        name = '[fragment-passthrough]%s' % urlencode(data)
        return u'<select name="%s">%s</select>' % (name, '\n'.join(options))
    
    def get_label(self, dotpath, value=None):
        if value:
            return escape(force_unicode(value))
        return self.render_type_dropdown(dotpath)

class TypedSchemaField(DotPathField):
    widget = TypedSchemaFieldWidget
    
    def __init__(self, *args, **kwargs):
        self.schema_property = kwargs.pop('schema_property')
        if hasattr(self.schema_property, 'subfield'):
            self.schema_property = self.schema_property.subfield
        super(TypedSchemaField, self).__init__(*args, **kwargs)
        self.widget.schema_property = self.schema_property

