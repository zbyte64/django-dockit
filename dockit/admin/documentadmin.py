from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse
from django.contrib.admin import widgets
from django import forms

from dockit.paginator import Paginator
from dockit.forms import DocumentForm
from dockit.forms.fields import PrimitiveListField

import views

FORMFIELD_FOR_FIELD_DEFAULTS = {
    forms.DateTimeField: {
        'form_class': forms.SplitDateTimeField,
        'widget': widgets.AdminSplitDateTime
    },
    forms.DateField:       {'widget': widgets.AdminDateWidget},
    forms.TimeField:       {'widget': widgets.AdminTimeWidget},
    #models.TextField:       {'widget': widgets.AdminTextareaWidget},
    #models.URLField:        {'widget': widgets.AdminURLFieldWidget},
    forms.IntegerField:    {'widget': widgets.AdminIntegerFieldWidget},
    #models.BigIntegerField: {'widget': widgets.AdminIntegerFieldWidget},
    forms.CharField:       {'widget': widgets.AdminTextInputWidget},
    forms.ImageField:      {'widget': widgets.AdminFileWidget},
    forms.FileField:       {'widget': widgets.AdminFileWidget},
}

class SchemaAdmin(object):
    #class based views
    create = views.CreateView
    update = views.UpdateView
    delete = views.DeleteView
    select_schema = views.SchemaTypeSelectionView
    
    raw_id_fields = ()
    fields = None
    exclude = []
    fieldsets = None
    form = forms.ModelForm #only for legacy purposes, remove this and django admin complains
    form_class = None
    filter_vertical = ()
    filter_horizontal = ()
    radio_fields = {}
    prepopulated_fields = {}
    formfield_overrides = {}
    readonly_fields = ()
    declared_fieldsets = None
    
    save_as = False
    save_on_top = False
    paginator = Paginator
    inlines = []

    # Custom templates (designed to be over-ridden in subclasses)
    add_form_template = None
    change_form_template = None
    change_list_template = None
    delete_confirmation_template = None
    delete_selected_confirmation_template = None
    object_history_template = None
    
    schema = None

    def __init__(self, model, admin_site, schema=None, documentadmin=None):
        self.model = model
        self.admin_site = admin_site
        self.app_name = (model._meta.app_label +'_'+ model._meta.object_name).lower()
        overrides = FORMFIELD_FOR_FIELD_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides
        self.schema = schema
        self.documentadmin = documentadmin
        
    def get_view_kwargs(self):
        return {'admin':self,
                'admin_site':self.admin_site,}
    
    def _media(self):
        from django.conf import settings
        from django import forms

        js = ['js/core.js', 'js/admin/RelatedObjectLookups.js',
              'js/jquery.min.js', 'js/jquery.init.js']
        #if self.actions is not None:
        #    js.extend(['js/actions.min.js'])
        if self.prepopulated_fields:
            js.append('js/urlify.js')
            js.append('js/prepopulate.min.js')
        #if self.opts.get_ordered_objects():
        #    js.extend(['js/getElementsBySelector.js', 'js/dom-drag.js' , 'js/admin/ordering.js'])

        return forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url_s) for url_s in js])
    media = property(_media)
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def as_view(self, view, cacheable=False):
        return self.admin_site.admin_view(view, cacheable)
    
    def get_create_view(self):
        kwargs = self.get_view_kwargs()
        return self.as_view(self.create.as_view(**kwargs))
    
    def get_update_view(self):
        kwargs = self.get_view_kwargs()
        return self.as_view(self.update.as_view(**kwargs))
    
    def get_select_schema_view(self):
        kwargs = self.get_view_kwargs()
        kwargs['schema'] = self.schema
        return self.as_view(self.select_schema.as_view(**kwargs))
    
    def get_model_perms(self, request):
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
        }
    
    def queryset(self, request):
        return self.model.objects.all()
    
    def get_form_class(self, request, obj=None):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        else:
            return DocumentForm
    
    def _get_schema_fields(self):
        for field in self.schema._meta.fields.itervalues():
            if getattr(field, 'schema', None):
                yield (field, field.schema, False)
            elif getattr(field, 'subfield', None) and getattr(field.subfield, 'schema', None):
                yield (field, field.subfield.schema, True)
    
    def _get_static_schema_fields(self):
        fields = list()
        for field, schema, many in self._get_schema_fields():
            if not schema._meta.is_dynamic():
                fields.append((field, schema, many))
        return fields
    
    def get_excludes(self):
        excludes = set(self.exclude)
        excludes.update([inline.dotpath for inline in self.inlines])
        excludes.update([field.name for field, schema, many in self._get_static_schema_fields()])
        return list(excludes)
    
    def get_inline_instances(self):
        inline_instances = list()
        seen = set()
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site, None, self.documentadmin)
            inline_instances.append(inline_instance)
            seen.add(inline_instance.dotpath)
        
        #TODO how to overide?
        from inlines import StackedInline
        for field, schema, many in self._get_static_schema_fields():
            if field.name in seen:
                continue
            kwargs = {'dotpath':field.name + '.*'}
            if not many:
                kwargs['max_num'] = 1
            inline_instance = StackedInline(self.model, self.admin_site, schema, self.documentadmin, **kwargs)
            inline_instances.append(inline_instance)
        
        return inline_instances
    
    def get_formsets(self, request, obj=None):
        inline_instances = self.get_inline_instances()
        for inline in inline_instances:
            yield inline.get_formset(request, obj)
    
    def get_fieldsets(self, request, obj=None):
        "Hook for specifying fieldsets for the add form."
        if self.declared_fieldsets:
            return self.declared_fieldsets
        #form = self.get_form(request, obj)
        #fields = form.base_fields.keys() + list(self.get_readonly_fields(request, obj))
        fields = list()
        for key, field in self.schema._meta.fields.iteritems():
            fields.append(key) #TODO handle exclude
        return [(None, {'fields': fields})]
    
    def formfield_for_field(self, prop, field, view, **kwargs):
        import dockit
        from fields import DotPathField
        from dockit.forms.fields import HiddenJSONField
        request = kwargs.pop('request', None)
        if ((isinstance(prop, dockit.ListField) and isinstance(prop.subfield, dockit.TypedSchemaField)) or
             isinstance(prop, dockit.TypedSchemaField)):
            from fields import TypedSchemaField
            field = TypedSchemaField
            kwargs['dotpath'] = view.dotpath()
            kwargs['schema_property'] = prop
            if self.next_dotpath():
                kwargs['required'] = False
            return field(**kwargs)
        if issubclass(field, HiddenJSONField):
            field = DotPathField
            kwargs['dotpath'] = view.dotpath()
            if view.next_dotpath():
                kwargs['required'] = False
            return field(**kwargs)
        if issubclass(field, PrimitiveListField) and 'subfield' in kwargs:
            subfield_kwargs = dict(kwargs)
            subfield = self.formfield_for_field(prop, type(subfield_kwargs.pop('subfield')), view, **subfield_kwargs)
            kwargs['subfield'] = subfield
        if field in self.formfield_overrides:
            opts = dict(self.formfield_overrides[field])
            field = opts.pop('form_class', field)
            kwargs = dict(opts, **kwargs)
        return field(**kwargs)
    
    def log_addition(self, request, object):
        return self.documentadmin.log_addition(request, object)
    
    def log_change(self, request, object, message):
        return self.documentadmin.log_change(request, object, message)
    
    def log_deletion(self, request, object, object_repr):
        return self.documentadmin.log_deletion(request, object, object_repr)
    
    def reverse(self, name, *args, **kwargs):
        return self.documentadmin.reverse(name, *args, **kwargs)
    
    def get_readonly_fields(self, request, schema=None):
        schema = schema or self.schema
        read_only = list()
        for key, field in schema._meta.fields.iteritems():
            if not field.editable:
                read_only.append(key)
        return read_only
    
class DocumentAdmin(SchemaAdmin):
    list_display = ('__str__',)
    list_display_links = ()
    list_filter = ()
    list_select_related = False
    list_per_page = 100
    list_editable = ()
    search_fields = ()
    date_hierarchy = None
    ordering = None
    
    # Actions
    actions = []
    #action_form = helpers.ActionForm
    actions_on_top = True
    actions_on_bottom = False
    actions_selection_counter = True
    
    #the following proxy to the proper schema admin
    create = views.DocumentProxyView
    update = views.DocumentProxyView
    
    delete = views.DeleteView
    index = views.IndexView
    history = views.HistoryView
    detail_views = [views.HistoryView, views.DeleteView]
    default_schema_admin = SchemaAdmin
    schema_inlines = [] # [(Schema, SchemaAdminCls),]
    
    def get_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.as_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        
        init = self.get_view_kwargs()
        
        # Admin-site-wide views.
        urlpatterns = self.get_extra_urls()
        urlpatterns += patterns('',
            url(r'^$',
                wrap(self.index.as_view(**init)),
                name=self.app_name+'_changelist'),
            url(r'^add/$',
                wrap(self.create.as_view(**init)),
                name=self.app_name+'_add'),
        )
        
        for key, view in self.get_detail_views().iteritems():
            url_p = r'^(?P<pk>.+)/%s/$' % key
            if hasattr(view, 'get_url_pattern'):
                url_p = view.get_url_pattern(self)
            urlpatterns += patterns('',
                url(url_p,
                    wrap(view.as_view(**init)),
                    name='%s_%s' % (self.app_name, key)),
            )
        
        urlpatterns += patterns('', #we shouldn't put anything after this url
            url(r'^(?P<pk>.+)/$',
                wrap(self.update.as_view(**init)),
                name=self.app_name+'_change'),
        )
        return urlpatterns
    
    def urls(self):
        return self.get_urls(), self.app_name, None
    urls = property(urls)
    
    def get_extra_urls(self):
        return patterns('',)
    
    def get_detail_views(self):
        ret = dict()
        for detail_view in self.detail_views:
            ret[detail_view.key] = detail_view
        return ret
    
    def get_changelist(self, request):
        from changelist import ChangeList
        return ChangeList
    
    def get_paginator(self, request, query_set, paginate_by):
        return self.paginator(query_set, paginate_by)
    
    def reverse(self, name, *args, **kwargs):
        from django.core.urlresolvers import get_urlconf, get_resolver
        urlconf = get_urlconf()
        resolver = get_resolver(urlconf)
        app_list = resolver.app_dict['admin']
        return reverse('%s:%s' % (self.admin_site.name, name), args=args, kwargs=kwargs, current_app=self.app_name)
    
    def create_admin_for_schema(self, schema):
        admin_class = self.get_admin_class_for_schema(schema)
        return admin_class(self.model, self.admin_site, schema, self)
    
    def get_admin_class_for_schema(self, schema):
        for cls, admin_class in self.schema_inlines:
            if schema == cls:
                return admin_class
        return self.default_schema_admin
    
    def log_addition(self, request, object):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, ADDITION
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            #content_type_id = ContentType.objects.get_for_model(object).pk,
            content_type_id = None,
            object_id       = object.get_id(),
            object_repr     = force_unicode(object),
            action_flag     = ADDITION
        )
    
    def log_change(self, request, object, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, CHANGE
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            #content_type_id = ContentType.objects.get_for_model(object).pk,
            content_type_id = None,
            object_id       = object.get_id(),
            object_repr     = force_unicode(object),
            action_flag     = CHANGE,
            change_message  = message
        )
    
    def log_deletion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method is called
        before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, DELETION
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            #content_type_id = ContentType.objects.get_for_model(self.model).pk,
            content_type_id = None,
            object_id       = object.get_id(),
            object_repr     = object_repr,
            action_flag     = DELETION
        )


'''
crud request -> DocumentAdmin
DocumentAdmin -> DocumentProxyView
DocumentProxyView
'''

'''
bring back inlines with a vengance

StackedInline, TabularInline, FieldInline

admin excludes these fields, need to get inlines for schema
2nd pass could get rid of some nasty hacks

django admin is strict about inlines, may need to implement under a different name
inline.get_formset => powerhouse, basic formset support is all that is needed

CONSIDER: may want to create new admin instance for a subschema, like get_view_for_schema...
what other sane strategies are there?
'''

