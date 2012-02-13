from django.forms.widgets import Widget, Media, HiddenInput
from django.utils.safestring import mark_safe
import django.utils.copycompat as copy

class PrimitiveListWidget(Widget):
    '''
    Wraps around a subfield
    The widget receives the subfield and is responsible for rendering multiple iterations of the subfield and collecting of data
    '''
    def __init__(self, subfield, attrs=None):
        self.subfield = subfield
        super(PrimitiveListWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        #if self.is_localized:
        #    self.widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        i = -1
        for i, widget_value in enumerate(value):
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(self.subfield.widget.render(name + '_%s' % i, widget_value, final_attrs))
        output.append(self.subfield.widget.render(name + '_%s' % (i+1), None, final_attrs))
        output.append(HiddenInput().render(name + '_count', str(i+1), {}))
        return mark_safe(self.format_output(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        count = int(data.get(name + '_count', 0))
        ret = list()
        for i in range(count):
            val = self.subfield.widget.value_from_datadict(data, files, '%s_%s' % (name, i))
            ret.append(val)
        return ret

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

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), returns a Unicode string
        representing the HTML for the whole lot.

        This hook allows you to format the HTML design of the widgets, if
        needed.
        """
        
        return '<table><tr><td>%s</td></tr></table>' % u'</td></tr><tr><td>'.join(rendered_widgets)

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
        return media
    media = property(_get_media)

    def __deepcopy__(self, memo):
        obj = super(PrimitiveListWidget, self).__deepcopy__(memo)
        obj.subfield = copy.deepcopy(self.subfield)
        return obj
