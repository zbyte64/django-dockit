from django.forms.widgets import Widget, Media, HiddenInput
from django.utils.safestring import mark_safe
import django.utils.copycompat as copy

class PrimitiveListWidget(Widget):
    """
    A widget that is composed of multiple widgets.

    Its render() method is different than other widgets', because it has to
    figure out how to split a single value for display in multiple widgets.
    The ``value`` argument can be one of two things:

        * A list.
        * A normal value (e.g., a string) that has been "compressed" from
          a list of values.

    In the second case -- i.e., if the value is NOT a list -- render() will
    first "decompress" the value into a list before rendering it. It does so by
    calling the decompress() method, which MultiWidget subclasses must
    implement. This method takes a single "compressed" value and returns a
    list.

    When render() does its HTML rendering, each value in the list is rendered
    with the corresponding widget -- the first value is rendered in the first
    widget, the second value is rendered in the second widget, etc.

    Subclasses may implement format_output(), which takes the list of rendered
    widgets and returns a string of HTML that formats them any way you'd like.

    You'll probably want to use this class with MultiValueField.
    """
    def __init__(self, widget, attrs=None):
        if isinstance(widget, type):
            widget = widget()
        self.widget = widget
        super(PrimitiveListWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            self.widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        i = 0
        for i, widget_value in enumerate(value):
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(self.widget.render(name + '_%s' % i, widget_value, final_attrs))
        output.append(self.widget.render(name + '_%s' % (i+1), None, final_attrs))
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
            val = self.widget.value_from_datadict(data, files, '%s_%s' % (name, i))
            ret.append(val)
        return ret

    def _has_changed(self, initial, data):
        if initial is None:
            initial = [u'' for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.decompress(initial)
        print data
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
        return u''.join(rendered_widgets)

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
        for w in self.widgets:
            media = media + w.media
        return media
    media = property(_get_media)

    def __deepcopy__(self, memo):
        obj = super(PrimitiveListWidget, self).__deepcopy__(memo)
        obj.widget = copy.deepcopy(self.widget)
        return obj
