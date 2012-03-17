from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse
from django.contrib.admin import widgets
from django.contrib.admin.options import get_ul_class
from django import forms

from dockit.paginator import Paginator
from dockit.forms import DocumentForm
from dockit.forms.fields import PrimitiveListField

import views
from widgets import AdminPrimitiveListWidget
from breadcrumbs import Breadcrumb

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
    field_list_index = views.ListFieldIndexView
    
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
    
    #list display options
    list_display = ('__str__',)
    list_display_links = ()
    list_filter = ()
    list_select_related = False
    list_per_page = 100
    list_editable = ()
    search_fields = ()
    date_hierarchy = None
    ordering = None

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
        self.app_name = model._meta.app_label +'_'+ model._meta.module_name
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
    
    def get_create_view(self, **kwargs):
        params = self.get_view_kwargs()
        params.update(kwargs)
        return self.as_view(self.create.as_view(**params))
    
    def get_update_view(self, **kwargs):
        params = self.get_view_kwargs()
        params.update(kwargs)
        return self.as_view(self.update.as_view(**params))
    
    def get_select_schema_view(self, **kwargs):
        params = self.get_view_kwargs()
        params['schema'] = self.schema
        params.update(kwargs)
        return self.as_view(self.select_schema.as_view(**params))
    
    def get_field_list_index_view(self, **kwargs):
        params = self.get_view_kwargs()
        params.update(kwargs)
        return self.as_view(self.field_list_index.as_view(**params))
    
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
    
    def get_default_inline_instances(self, exclude=[]):
        inline_instances = list()
        from inlines import StackedInline
        for field, schema, many in self._get_static_schema_fields():
            if field.name in exclude:
                continue
            kwargs = {'dotpath':field.name + '.*'}
            if not many:
                kwargs['max_num'] = 1
                kwargs['dotpath'] = field.name
            inline_instance = StackedInline(self.model, self.admin_site, schema, self.documentadmin, **kwargs)
            inline_instances.append(inline_instance)
        return inline_instances
    
    def get_inline_instances(self):
        inline_instances = list()
        seen = set()
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site, None, self.documentadmin)
            inline_instances.append(inline_instance)
            seen.add(inline_instance.dotpath)
        
        inline_instances.extend(self.get_default_inline_instances(exclude=seen))
        
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
        from dockit import schema
        from fields import DotPathField
        from dockit.forms.fields import HiddenJSONField
        
        if isinstance(prop, schema.ModelReferenceField):
            return self.formfield_for_foreignkey(prop, field, view, **kwargs)
        if isinstance(prop, schema.ModelSetField):
            return self.formfield_for_manytomany(prop, field, view, **kwargs)
        
        request = kwargs.pop('request', None)
        base_property = prop
        if isinstance(prop, schema.ListField):
            base_property = prop.subfield
        
        #TODO self.raw_id_fields
        #TODO ForeignKeyRawIdWidget => DocumentReferenceRawIdWidget
        if prop.name in self.raw_id_fields:
            if isinstance(prop, schema.ReferenceField):
                pass
            elif isinstance(prop, schema.ModelReferenceField):
                pass
        
        if (isinstance(base_property, schema.TypedSchemaField) or 
             (isinstance(base_property, schema.SchemaField) and base_property.schema._meta.typed_field)):
            from fields import TypedSchemaField
            field = TypedSchemaField
            kwargs['dotpath'] = view.dotpath()
            kwargs['params'] = request.GET.copy()
            if isinstance(base_property, schema.SchemaField):
                type_selector = base_property.schema._meta.fields[base_property.schema._meta.typed_field]
            else:
                type_selector = base_property
            kwargs['schema_property'] = type_selector
            if view.next_dotpath():
                kwargs['required'] = False
            return field(**kwargs)
        if issubclass(field, HiddenJSONField):
            field = DotPathField
            kwargs['dotpath'] = view.dotpath()
            kwargs['params'] = request.GET.copy()
            if view.next_dotpath():
                kwargs['required'] = False
            return field(**kwargs)
        if issubclass(field, PrimitiveListField) and 'subfield' in kwargs:
            subfield_kwargs = dict(kwargs)
            subfield_kwargs.pop('initial', None)
            subfield = self.formfield_for_field(prop, type(subfield_kwargs.pop('subfield')), view, **subfield_kwargs)
            kwargs['subfield'] = subfield
            kwargs['widget'] = AdminPrimitiveListWidget
        if field in self.formfield_overrides:
            opts = dict(self.formfield_overrides[field])
            field = opts.pop('form_class', field)
            kwargs = dict(opts, **kwargs)
        return field(**kwargs)
    
    def formfield_for_foreignkey(self, prop, field, view, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        request = kwargs.pop('request', None)
        if prop.name in self.raw_id_fields:
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget(rel=None)
        elif prop.name in self.radio_fields:
            kwargs['widget'] = widgets.AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[prop.name]),
            })
            kwargs['empty_label'] = prop.blank and _('None') or None

        return prop.formfield(**kwargs)

    def formfield_for_manytomany(self, prop, field, view, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        request = kwargs.pop('request', None)
        if prop.name in self.raw_id_fields:
            kwargs['widget'] = widgets.ManyToManyRawIdWidget(rel=None)
            kwargs['help_text'] = ''
        elif prop.name in (list(self.filter_vertical) + list(self.filter_horizontal)):
            kwargs['widget'] = widgets.FilteredSelectMultiple(prop.verbose_name, (prop.name in self.filter_vertical))

        return prop.formfield(**kwargs)
    
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
    
    def get_paginator(self, request, query_set, paginate_by):
        return self.paginator(query_set, paginate_by)
    
    def get_object_tools(self, request, object=None):
        #TODO object tools are renderable object that are displayed at the top the admin
        #TODO return history object tool if there is an object
        return []
    
    def get_field(self, schema, dotpath, obj=None):
        field = None
        if dotpath and obj:
            field = obj.dot_notation_to_field(dotpath)
            if field is None:
                parent_path = dotpath.rsplit('.', 1)[0]
                print 'no field', dotpath, obj
                
                from dockit.schema.common import DotPathTraverser
                traverser = DotPathTraverser(parent_path)
                traverser.resolve_for_instance(obj)
                info = traverser.resolved_paths
                subschema = info[2]['field'].schema
                fields = subschema._meta.fields
                
                field = obj.dot_notation_to_field(parent_path)
                data = obj._primitive_data
                assert field
        return field
    
    def get_base_breadcrumbs(self):
        return self.documentadmin.get_base_breadcrumbs()
    
    def get_instance_breadcrumb(self, obj=None):
        return self.documentadmin.get_instance_breadcrumb(obj)

class DocumentAdmin(SchemaAdmin):
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
    
    def reverse(self, name, *args, **kwargs):
        from django.core.urlresolvers import get_urlconf, get_resolver
        urlconf = get_urlconf()
        resolver = get_resolver(urlconf)
        app_list = resolver.app_dict['admin']
        return reverse('%s:%s' % (self.admin_site.name, name), args=args, kwargs=kwargs, current_app=self.app_name)
    
    def create_admin_for_schema(self, schema, object=None):
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
    
    def get_base_breadcrumbs(self):
        admin_name = self.admin_site.name
        model_name = self.model._meta.verbose_name
        opts = self.model._meta
        breadcrumbs = [
            Breadcrumb('Home', ['%s:index' % admin_name]),
            Breadcrumb(opts.app_label, ['%s:app_list' % admin_name, (self.app_name,), {}]),
            Breadcrumb(opts.verbose_name_plural, ['%s:%s_changelist' % (admin_name, self.app_name)]),
        ]
        return breadcrumbs
    
    def get_instance_breadcrumb(self, obj=None):
        if obj:
            return Breadcrumb(unicode(obj))
        return Breadcrumb('Add %s' % self.model._meta.verbose_name)
    
    def has_add_permission(self, request):
        opts = self.model._meta
        #print opts.collection, request.user.has_perm('dockit.'+ opts.get_add_permission()), opts.get_add_permission()
        #print request.user.user_permissions.all().filter(codename=opts.get_add_permission()).values_list('codename', 'content_type')
        return request.user.has_perm('dockit.'+ opts.get_add_permission())
    
    def has_change_permission(self, request, obj=None):
        opts = self.model._meta
        return request.user.has_perm('dockit.'+ opts.get_change_permission(), obj)
    
    def has_delete_permission(self, request, obj=None):
        opts = self.model._meta
        return request.user.has_perm('dockit.'+ opts.get_delete_permission(), obj)

