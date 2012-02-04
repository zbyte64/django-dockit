from django.contrib.admin.helpers import InlineAdminFormSet as BaseInlineAdminFormSet, AdminField, normalize_fieldsets

from django import forms
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.html import escape, conditional_escape
from django.contrib.admin.util import (flatten_fieldsets, lookup_field,
    display_for_field, label_for_field, help_text_for_field)
from django.forms.util import flatatt
from django.template.defaultfilters import capfirst
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist

class AdminForm(object):
    def __init__(self, form, fieldsets, prepopulated_fields, readonly_fields=None, model_admin=None):
        self.form, self.fieldsets = form, normalize_fieldsets(fieldsets)
        self.prepopulated_fields = [{
            'field': form[field_name],
            'dependencies': [form[f] for f in dependencies]
        } for field_name, dependencies in prepopulated_fields.items()]
        self.model_admin = model_admin
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __iter__(self):
        for name, options in self.fieldsets:
            yield Fieldset(self.form, name,
                readonly_fields=self.readonly_fields,
                model_admin=self.model_admin,
                **options
            )

    def first_field(self):
        try:
            fieldset_name, fieldset_options = self.fieldsets[0]
            field_name = fieldset_options['fields'][0]
            if not isinstance(field_name, basestring):
                field_name = field_name[0]
            return self.form[field_name]
        except (KeyError, IndexError):
            pass
        try:
            return iter(self.form).next()
        except StopIteration:
            return None

    def _media(self):
        media = self.form.media
        for fs in self:
            media = media + fs.media
        return media
    media = property(_media)


class Fieldset(object):
    def __init__(self, form, name=None, readonly_fields=(), fields=(), classes=(),
      description=None, model_admin=None):
        self.form = form
        self.name, self.fields = name, fields
        self.classes = u' '.join(classes)
        self.description = description
        self.model_admin = model_admin
        self.readonly_fields = readonly_fields

    def _media(self):
        if 'collapse' in self.classes:
            js = ['js/jquery.min.js', 'js/jquery.init.js', 'js/collapse.min.js']
            return forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in js])
        return forms.Media()
    media = property(_media)

    def __iter__(self):
        for field in self.fields:
            yield Fieldline(self.form, field, self.readonly_fields, model_admin=self.model_admin)

class Fieldline(object):
    def __init__(self, form, field, readonly_fields=None, model_admin=None):
        self.form = form # A django.forms.Form instance
        if not hasattr(field, "__iter__"):
            self.fields = [field]
        else:
            self.fields = field
        self.model_admin = model_admin
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __iter__(self):
        for i, field in enumerate(self.fields):
            if field in self.readonly_fields:
                yield AdminReadonlyField(self.form, field, is_first=(i == 0),
                    model_admin=self.model_admin)
            else:
                yield AdminField(self.form, field, is_first=(i == 0))

    def errors(self):
        return mark_safe(u'\n'.join([self.form[f].errors.as_ul() for f in self.fields if f not in self.readonly_fields]).strip('\n'))

class AdminReadonlyField(object):
    def __init__(self, form, field, is_first, model_admin=None):
        label = label_for_field(field, form._meta.schema, model_admin)
        # Make self.field look a little bit like a field. This means that
        # {{ field.name }} must be a useful class name to identify the field.
        # For convenience, store other field-related data here too.
        if callable(field):
            class_name = field.__name__ != '<lambda>' and field.__name__ or ''
        else:
            class_name = field
        self.field = {
            'name': class_name,
            'label': label,
            'field': field,
            'help_text': help_text_for_field(class_name, form._meta.schema)
        }
        self.form = form
        self.model_admin = model_admin
        self.is_first = is_first
        self.is_checkbox = False
        self.is_readonly = True

    def label_tag(self):
        attrs = {}
        if not self.is_first:
            attrs["class"] = "inline"
        label = self.field['label']
        contents = capfirst(force_unicode(escape(label))) + u":"
        return mark_safe('<label%(attrs)s>%(contents)s</label>' % {
            "attrs": flatatt(attrs),
            "contents": contents,
        })

    def contents(self):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon
        from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
        field, obj, model_admin = self.field['field'], self.form.instance, self.model_admin
        try:
            f, attr, value = lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            result_repr = EMPTY_CHANGELIST_VALUE
        else:
            if f is None:
                boolean = getattr(attr, "boolean", False)
                if boolean:
                    result_repr = _boolean_icon(value)
                else:
                    result_repr = smart_unicode(value)
                    if getattr(attr, "allow_tags", False):
                        result_repr = mark_safe(result_repr)
            else:
                if value is None:
                    result_repr = EMPTY_CHANGELIST_VALUE
                elif isinstance(f.rel, ManyToManyRel):
                    result_repr = ", ".join(map(unicode, value.all()))
                else:
                    result_repr = display_for_field(value, f)
        return conditional_escape(result_repr)

class InlineFieldset(Fieldset):
    def __init__(self, formset, *args, **kwargs):
        self.formset = formset
        super(InlineFieldset, self).__init__(*args, **kwargs)

    def __iter__(self):
        for field in self.fields:
            yield Fieldline(self.form, field, self.readonly_fields,
                model_admin=self.model_admin)

class InlineAdminForm(AdminForm):
    """
    A wrapper around an inline form for use in the admin system.
    """
    def __init__(self, formset, form, fieldsets, prepopulated_fields, original,
      readonly_fields=None, model_admin=None):
        self.formset = formset
        self.model_admin = model_admin
        self.original = original
        self.show_url = original and hasattr(original, 'get_absolute_url')
        super(InlineAdminForm, self).__init__(form, fieldsets, prepopulated_fields,
            readonly_fields, model_admin)

    def __iter__(self):
        for name, options in self.fieldsets:
            yield InlineFieldset(self.formset, self.form, name,
                self.readonly_fields, model_admin=self.model_admin, **options)

    def has_auto_field(self):
        return False

    def field_count(self):
        # tabular.html uses this function for colspan value.
        num_of_fields = 0
        if self.has_auto_field():
            num_of_fields += 1
        num_of_fields += len(self.fieldsets[0][1]["fields"])
        if self.formset.can_order:
            num_of_fields += 1
        if self.formset.can_delete:
            num_of_fields += 1
        return num_of_fields

    def pk_field(self):
        return AdminField(self.form, self.formset._pk_field.name, False)

    def fk_field(self):
        fk = getattr(self.formset, "fk", None)
        if fk:
            return AdminField(self.form, fk.name, False)
        else:
            return ""

    def deletion_field(self):
        from django.forms.formsets import DELETION_FIELD_NAME
        return AdminField(self.form, DELETION_FIELD_NAME, False)

    def ordering_field(self):
        from django.forms.formsets import ORDERING_FIELD_NAME
        return AdminField(self.form, ORDERING_FIELD_NAME, False)

class InlineAdminFormSet(BaseInlineAdminFormSet):
    def __init__(self, inline, formset, fieldsets, readonly_fields=None, model_admin=None):
        self.opts = inline
        self.formset = formset
        self.fieldsets = fieldsets
        self.model_admin = model_admin
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __iter__(self):
        for form, original in zip(self.formset.initial_forms, self.formset.get_queryset()):
            yield InlineAdminForm(self.formset, form, self.fieldsets,
                self.opts.prepopulated_fields, original, self.readonly_fields,
                model_admin=self.opts)
        for form in self.formset.extra_forms:
            yield InlineAdminForm(self.formset, form, self.fieldsets,
                self.opts.prepopulated_fields, None, self.readonly_fields,
                model_admin=self.opts)
        yield InlineAdminForm(self.formset, self.formset.empty_form,
            self.fieldsets, self.opts.prepopulated_fields, None,
            self.readonly_fields, model_admin=self.opts)

    def fields(self):
        for i, field in enumerate(flatten_fieldsets(self.fieldsets)):
            if field in self.readonly_fields:
                yield {
                    'label': label_for_field(field, self.opts.model, self.opts),
                    'widget': {
                        'is_hidden': False
                    },
                    'required': False
                }
            else:
                yield self.formset.form.base_fields[field]

