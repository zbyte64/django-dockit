from django.http import HttpResponseRedirect, HttpResponse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.utils.html import escape, escapejs
from django.views.generic import TemplateView, View

from base import AdminViewMixin
from breadcrumbs import Breadcrumb
import helpers

from dockit import views
from dockit.models import create_temporary_document_class
from dockit.schema.fields import ListField
from dockit.schema.common import UnSet
from dockit.schema.schema import Schema

from urllib import urlencode
from urlparse import parse_qsl

CALL_BACK = "" #TODO

class DocumentViewMixin(AdminViewMixin):
    template_suffix = None
    template_name = None
    form_class = None
    object = None
    
    @property
    def document(self):
        return self.admin.model
    
    @property
    def schema(self):
        return self.admin.schema
    
    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        opts = self.document._meta
        app_label = opts.app_label
        object_name = opts.object_name.lower()
        return ['admin/%s/%s/%s.html' % (app_label, object_name, self.template_suffix),
                'admin/%s/%s.html' % (app_label, self.template_suffix),
                'admin/%s.html' % self.template_suffix]
    
    #def get_queryset(self):
    #    return self.model.objects.all()
    
    def get_breadcrumbs(self):
        return self.admin.get_base_breadcrumbs()
    
    def get_context_data(self, **kwargs):
        opts = self.document._meta
        obj = self.object
        context = AdminViewMixin.get_context_data(self, **kwargs)
        context.update({'root_path': self.admin_site.root_path,
                        'app_label': opts.app_label,
                        'opts': opts,
                        'module_name': force_unicode(opts.verbose_name_plural),
                        'breadcrumbs': self.get_breadcrumbs(),
                        'has_add_permission': self.admin.has_add_permission(self.request),
                        'has_change_permission': self.admin.has_change_permission(self.request, obj),
                        'has_delete_permission': self.admin.has_delete_permission(self.request, obj),
                        'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
                        'has_absolute_url': hasattr(self.document, 'get_absolute_url'),
                        #'content_type_id': ContentType.objects.get_for_model(self.model).id,
                        'save_as': self.admin.save_as,
                        'save_on_top': self.admin.save_on_top,})
        return context

class BaseFragmentViewMixin(DocumentViewMixin):
    def is_polymorphic(self, schema):
        return bool(schema._meta.typed_field)
    
    def should_prompt_polymorphic_type(self, schema, obj=None):
        if self.is_polymorphic(schema):
            foo = schema._meta.typed_field
            return obj is None or not getattr(obj, schema._meta.typed_field, None)
        return False
    
    def needs_typed_selection(self, schema, obj=None):
        if schema._meta.typed_field and schema._meta.typed_field in self.request.GET:
            return False
        return self.should_prompt_polymorphic_type(schema, obj)
    
    def dotpath(self):
        return self.request.GET.get('_dotpath', None)
    
    def parent_dotpath(self):
        return self.request.GET.get('_parent_dotpath', None)
    
    def temporary_document_id(self):
        return self.request.GET.get('_tempdoc', None)
    
    def get_temporary_store(self):
        if not hasattr(self, '_temporary_store'):
            temp_doc_id = self.temporary_document_id()
            if temp_doc_id:
                storage = self.temp_document.objects.get(pk=temp_doc_id)
            else:
                if getattr(self, 'object', None):
                    storage = self.temp_document.create_from_instance(self.object)
                else:
                    storage = self.temp_document()
            self._temporary_store = storage
        return self._temporary_store
    
    def get_active_object(self):
        if self.dotpath():
            val = self.get_temporary_store()
            return val.dot_notation_to_value(self.dotpath())
        return self.get_temporary_store()
    
    @property
    def temp_document(self):
        if not hasattr(self, '_temp_document'):
            self._temp_document = create_temporary_document_class(self.document)
        return self._temp_document
    
    def get_breadcrumbs(self):
        breadcrumbs = DocumentViewMixin.get_breadcrumbs(self)
        obj = self.object
        breadcrumbs.append(self.admin.get_instance_breadcrumb(obj))
        return breadcrumbs

from forms import TypeSelectionForm

class SchemaTypeSelectionView(BaseFragmentViewMixin, TemplateView):
    template_name = 'admin/type_selection_form.html'
    form_class = TypeSelectionForm
    schema = None
    
    def get_form_class(self):
        return self.form_class
    
    def get_form_kwargs(self):
        assert self.schema
        return {'schema': self.schema,
                'initial':self.request.GET}
    
    def get_form(self, form_cls):
        return form_cls(**self.get_form_kwargs())
    
    def get_admin_form_kwargs(self):
        return {
            'fieldsets': [(None, {'fields': [self.schema._meta.typed_field]})],
            'prepopulated_fields': dict(),
            'readonly_fields': [],
            'model_admin': self.admin,
        }
    
    def create_admin_form(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        admin_form = helpers.AdminForm(form, **self.get_admin_form_kwargs())
        return admin_form
    
    def get_breadcrumbs(self):
        breadcrumbs = DocumentViewMixin.get_breadcrumbs(self)
        obj = getattr(self, 'object', None)
        breadcrumbs.append(self.admin.get_instance_breadcrumb(obj))
        if self.dotpath():
            breadcrumbs.append(Breadcrumb(self.dotpath()))
        return breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = DocumentViewMixin.get_context_data(self, **kwargs)
        context.update(TemplateView.get_context_data(self, **kwargs))
        context['adminform'] = self.create_admin_form()
        context['form_url'] = self.request.get_full_path()
        return context

class FragmentViewMixin(BaseFragmentViewMixin):
    template_suffix = 'schema_form'
    
    def create_admin_form(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        admin_form = helpers.AdminForm(form, **self.get_admin_form_kwargs())
        return admin_form
    
    def get_admin_form_kwargs(self):
        return {
            'fieldsets': self.get_fieldsets(),
            'prepopulated_fields': self.get_prepopulated_fields(),
            'readonly_fields': self.get_readonly_fields(),
            'model_admin': self.admin,
        }
    
    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        else:
            return self._generate_form_class()
    
    def get_readonly_fields(self):
        return self.admin.get_readonly_fields(self.request)
    
    def get_fieldsets(self, obj=None):
        "Hook for specifying fieldsets for the add form."
        form = self.get_form_class()
        fields = form.base_fields.keys()
        return [(None, {'fields': fields})]
    
    def get_prepopulated_fields(self):
        return self.admin.prepopulated_fields
    
    def get_formsets(self):
        formsets_cls = self.admin.get_formsets(self.request, self.get_active_object())
        
        prefixes = {}
        formsets = list()
        for FormSet, inline in zip(formsets_cls,
                                   self.admin.get_inline_instances()):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                kwargs = self.get_formset_kwargs()
                kwargs['prefix'] = prefix
                if self.dotpath():
                    kwargs['dotpath'] = self.dotpath() + '.' + inline.dotpath
                else:
                    kwargs['dotpath'] = inline.dotpath
                formset = FormSet(**kwargs)
                formsets.append(formset)
        return formsets
    
    def get_formset_kwargs(self):
        kwargs = self.get_form_kwargs()
        kwargs.pop('initial', None)
        return kwargs
    
    def get_inline_admin_formsets(self):
        formsets = self.get_formsets()
        obj = self.get_active_object()
        inline_admin_formsets = []
        for inline, formset in zip(self.admin.get_inline_instances(), formsets):
            fieldsets = list(inline.get_fieldsets(self.request))
            readonly = list(inline.get_readonly_fields(self.request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
        
        return inline_admin_formsets
    
    def get_breadcrumbs(self):
        breadcrumbs = BaseFragmentViewMixin.get_breadcrumbs(self)
        if self.dotpath():
            breadcrumbs.append(Breadcrumb(self.dotpath()))
        return breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = AdminViewMixin.get_context_data(self, **kwargs)
        opts = self.schema._meta
        context.update({'title': _('Add %s') % force_unicode(opts.verbose_name),
                        'show_save': True,
                        'show_delete_link': bool(self.dotpath()), #TODO is it a new subobject?
                        'show_save_and_add_another': False,
                        'show_save_and_continue': True,
                        'add': True,
                        'add_another': True,
                        'cancel': False,
                        'change': False,
                        'delete': False,
                        'breadcrumbs': self.get_breadcrumbs(),
                        'dotpath': self.dotpath(),
                        'tempdoc': self.get_temporary_store(),
                        'adminform':self.create_admin_form(),
                        'inline_admin_formsets': self.get_inline_admin_formsets(),})
        context['media'] += context['adminform'].form.media
        for inline in context['inline_admin_formsets']:
            context['media'] += inline.media
        
        obj = None
        if hasattr(self, 'object'):
            obj = self.object
        
        context.update({'root_path': self.admin_site.root_path,
                        'app_label': opts.app_label,
                        'opts': opts,
                        'original': obj,
                        'module_name': force_unicode(opts.verbose_name_plural),
                        'has_add_permission': self.admin.has_add_permission(self.request),
                        'has_change_permission': self.admin.has_change_permission(self.request, obj),
                        'has_delete_permission': self.admin.has_delete_permission(self.request, obj),
                        'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
                        'has_absolute_url': hasattr(self.document, 'get_absolute_url'),
                        #'content_type_id': ContentType.objects.get_for_model(self.model).id,
                        'save_as': self.admin.save_as,
                        'save_on_top': self.admin.save_on_top,})
        context['object_tools'] = self.get_object_tools(context)
        return context
    
    @property
    def form_class(self):
        return self.admin.form_class
    
    def fragment_info(self):
        token = '[fragment]'
        for key in self.request.POST.iterkeys():
            if key.startswith(token):
                info = dict(parse_qsl(key[len(token):]))
                if info:
                    return info
        return {}
    
    def fragment_passthrough(self):
        dotpath = self.next_dotpath()
        token = '[fragment-passthrough]'
        passthrough = dict()
        for key, value in self.request.POST.iteritems():
            if key.startswith(token):
                info = dict(parse_qsl(key[len(token):]))
                if info and info.pop('next_dotpath', None) == dotpath:
                    passthrough[info['name']] = value
        return passthrough
    
    def next_dotpath(self):
        info = self.fragment_info()
        return info.get('next_dotpath', None)
    
    def get_object_tools(self, context):
        object_tools = list()
        for object_tool in self.admin.get_object_tools(self.request):
            object_tools.append(object_tool.render(self.request, context))
        return object_tools
    
    def formfield_for_field(self, prop, field, **kwargs):
        return self.admin.formfield_for_field(prop, field, self, **kwargs)
    
    def get_base_schema(self):
        return self.admin.schema
    
    def get_schema(self):
        '''
        Retrieves the currently active schema, taking into account dynamic typing
        '''
        return self.get_base_schema()
    
    def _generate_form_class(self):
        form_cls = self.admin.get_form_class(self.request)
        
        class CustomDocumentForm(form_cls):
            class Meta:
                document = self.temp_document
                schema = self.get_schema()
                form_field_callback = self.formfield_for_field
                dotpath = self.dotpath() or None
                exclude = self.admin.get_excludes() + self.get_readonly_fields()
                #TODO fix readonly field behavior
        return CustomDocumentForm
    
    def get_form_kwargs(self, **kwargs):
        kwargs['instance'] = self.get_temporary_store()
        if self.request.method.upper() in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST
            kwargs['files'] = self.request.FILES
        if self.dotpath():
            kwargs['dotpath'] = self.dotpath()
        
        #populate typed field
        schema = self.get_schema()
        if schema._meta.typed_field and schema._meta.typed_field in self.request.GET:
            kwargs.setdefault('initial', {})
            kwargs['initial'][schema._meta.typed_field] = self.request.GET[schema._meta.typed_field]
        return kwargs
    
    def delete_subobject(self):
        temp = self.get_temporary_store()
        params = {'_tempdoc':temp.get_id(),}
        
        #TODO in FragmentViewMixin, get_effective_parent_dotpath()
        next_dotpath = self.parent_dotpath()
        if next_dotpath is None:
            dotpath = self.dotpath()
            if '.' in dotpath:
                next_dotpath = dotpath[:dotpath.rfind('.')]
            field = temp.dot_notation_to_field(next_dotpath)
            if isinstance(field, ListField):
                if '.' in next_dotpath:
                    next_dotpath = next_dotpath[:next_dotpath.rfind('.')]
                else:
                    next_dotpath = None
        
        if next_dotpath:
            params['_dotpath'] = next_dotpath
        #TODO make this a blessed function
        temp.dot_notation_set_value(self.dotpath(), UnSet)
        temp.save()
        return HttpResponseRedirect('%s?%s' % (self.admin.reverse(self.admin.app_name+'_change', self.kwargs['pk']), urlencode(params)))
    
    def post(self, request, *args, **kwargs):
        if self.dotpath() and "_delete" in self.request.POST:
            return self.delete_subobject()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.get_formsets()
        if not form.is_valid():
            return self.form_invalid(form)#, formsets)
        
        for formset in formsets:
            if not formset.is_valid():
                return self.form_invalid(form)#, formsets)
        
        obj = form.save(commit=False) #CONSIDER this would normally be done in form_valid
        for formset in formsets:
            formset.save(instance=obj)#form.target_object)
        obj.save()
        assert obj._meta.collection == self.temp_document._meta.collection
        
        
        if self.next_dotpath():
            info = self.fragment_info()
            passthrough = self.fragment_passthrough()
            params = {'_dotpath': self.next_dotpath(),
                      '_parent_dotpath': self.dotpath() or '',
                      '_tempdoc': obj.get_id(),}
            params.update(passthrough)
            return HttpResponseRedirect('%s?%s' % (request.path, urlencode(params)))
        if self.dotpath():
            params = {'_tempdoc':obj.get_id(),}
            
            #if they signaled to continue editing
            if self.request.POST.get('_continue', False):
                next_dotpath = self.dotpath()
            else:
                next_dotpath = self.parent_dotpath()
                if next_dotpath is None:
                    dotpath = self.dotpath()
                    if '.' in dotpath:
                        next_dotpath = dotpath[:dotpath.rfind('.')]
                    field = obj.dot_notation_to_field(next_dotpath)
                    if isinstance(field, ListField):
                        if '.' in next_dotpath:
                            next_dotpath = next_dotpath[:next_dotpath.rfind('.')]
                        else:
                            next_dotpath = None
            if next_dotpath:
                params['_dotpath'] = next_dotpath
            return HttpResponseRedirect('%s?%s' % (request.path, urlencode(params)))
        
        #now to create the object!
        if obj._meta.collection != self.document._meta.collection:
            self.object = obj.commit_changes(self.kwargs.get('pk', None))
        else:
            self.object = obj
        if 'pk' in self.kwargs:
            assert str(self.object.pk) == self.kwargs['pk']
        if self.temporary_document_id():
            self.get_temporary_store().delete()
        return self.form_valid(form)
    
    def form_valid(self, form):
        if "_popup" in self.request.POST:
            return HttpResponse(CALL_BACK % \
                # escape() calls force_unicode.
                {'value': escape(self.object.get_id()), 
                 'name': escapejs(self.document._meta.verbose_name)})
        if '_continue' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_change', self.object.get_id()))
        if '_addanother' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_add'))
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_changelist'))

class IndexView(DocumentViewMixin, views.ListView):
    template_suffix = 'change_list'
    
    def get_changelist(self):
        if not hasattr(self, 'changelist'):
            changelist_cls = self.admin.get_changelist(self.request)
            self.changelist = changelist_cls(request=self.request,
                                        model=self.document,
                                        list_display=self.admin.list_display,
                                        list_display_links=self.admin.list_display_links,
                                        list_filter=self.admin.list_filter,
                                        date_hierarchy=self.admin.date_hierarchy,
                                        search_fields=self.admin.search_fields,
                                        list_select_related=self.admin.list_select_related,
                                        list_per_page=self.admin.list_per_page,
                                        list_editable=self.admin.list_editable,
                                        model_admin=self.admin,)
        return self.changelist
    
    def get_context_data(self, **kwargs):
        context = views.ListView.get_context_data(self, **kwargs)
        context.update(DocumentViewMixin.get_context_data(self, **kwargs))
        cl = self.get_changelist()
        context.update({'cl': cl,
                        'title': cl.title,
                        'is_popup': cl.is_popup,})
        
        return context
    
    def get_queryset(self):
        cl = self.get_changelist()
        return cl.get_query_set()

class ListFieldIndexView(BaseFragmentViewMixin, views.DetailView):
    template_suffix = 'listfield_change_list'
    
    def get_changelist_class(self):
        from changelist import ListFieldChangeList
        return ListFieldChangeList
    
    def get_changelist(self):
        if not hasattr(self, 'changelist'):
            instance = self.get_temporary_store()
            dotpath = self.dotpath()
            changelist_cls = self.get_changelist_class()
            #CONSIDER: schemaadmin should have these values
            self.changelist = changelist_cls(request=self.request,
                                        model=self.schema,
                                        instance=instance,
                                        dotpath=dotpath,
                                        list_display=self.admin.list_display,
                                        list_display_links=self.admin.list_display_links,
                                        list_filter=self.admin.list_filter,
                                        date_hierarchy=self.admin.date_hierarchy,
                                        search_fields=self.admin.search_fields,
                                        list_select_related=self.admin.list_select_related,
                                        list_per_page=self.admin.list_per_page,
                                        list_editable=self.admin.list_editable,
                                        model_admin=self.admin,)
        return self.changelist
    
    def get_breadcrumbs(self):
        breadcrumbs = BaseFragmentViewMixin.get_breadcrumbs(self)
        breadcrumbs.append(Breadcrumb(self.dotpath()))
        return breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = views.DetailView.get_context_data(self, **kwargs)
        context.update(BaseFragmentViewMixin.get_context_data(self, **kwargs))
        cl = self.get_changelist()
        context.update({'cl': cl,
                        'title': cl.title,
                        'is_popup': cl.is_popup,})
        context['object_list'] = cl.get_query_set()
        
        params = self.request.GET.copy()
        params['_dotpath'] = '%s.%s' % (params['_dotpath'], len(context['object_list']))
        context['add_link'] = './?%s' % params.urlencode()
        
        return_dotpath = self.dotpath()
        if '.' in return_dotpath:
            return_dotpath = return_dotpath.rsplit('.', 1)[0]
        else:
            return_dotpath = ''
        params['_dotpath'] = return_dotpath
        context['return_link'] = './?%s' % params.urlencode()
        return context

class DocumentProxyView(BaseFragmentViewMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = request
        self.object = self.get_object()
        schema = self.get_base_schema()
        
        if not self.dotpath() and self.needs_typed_selection(schema, self.get_temporary_store()):
            admin = self.admin.create_admin_for_schema(schema)
            return admin.get_select_schema_view(object=self.object)(request, *args, **kwargs)
        
        schema = self.get_schema()
        admin = self.admin.create_admin_for_schema(schema)
        field = self.get_field()
        
        #detect list field
        if field and isinstance(field, ListField):
            return admin.get_field_list_index_view(object=self.object)(request, *args, **kwargs)
        
        if 'pk' in kwargs:
            return admin.get_update_view(object=self.object)(request, *args, **kwargs)
        else:
            return admin.get_create_view(object=self.object)(request, *args, **kwargs)
    
    def get_base_schema(self):
        '''
        Retrieves base schema, taking into account dynamic typing
        '''
        schema = self.admin.model
        if schema._meta.typed_field:
            field = schema._meta.fields[schema._meta.typed_field]
            if schema._meta.typed_field in self.request.GET:
                key = self.request.GET[schema._meta.typed_field]
                try:
                    schema = field.schemas[key]
                except KeyError:
                    #TODO emit a warning
                    pass
            else:
                if self.temporary_document_id():
                    obj = self.get_temporary_store()
                else:
                    obj = self.object
                if obj:
                    try:
                        schema = field.schemas[obj[schema._meta.typed_field]]
                    except KeyError:
                        #TODO emit a warning
                        pass
            #KeyErrors cause the base schema to return, this should cause needs_typed_selection to return true
        return schema
    
    def get_field(self):
        return self.admin.get_field(self.get_base_schema(), self.dotpath(), self.get_temporary_store())
    
    def get_schema(self):
        '''
        Retrieves the currently active schema, taking into account dynamic typing
        '''
        schema = None
        
        if self.dotpath():
            field = self.get_field()
            if getattr(field, 'subfield', None):
                field = field.subfield
            if getattr(field, 'schema'):
                schema = field.schema
                if schema._meta.typed_field:
                    typed_field = schema._meta.fields[schema._meta.typed_field]
                    if schema._meta.typed_field in self.request.GET:
                        key = self.request.GET[schema._meta.typed_field]
                        schema = typed_field.schemas[key]
                    else:
                        obj = self.get_active_object()
                        if obj is not None and isinstance(obj, Schema):
                            schema = type(obj)
            else:
                assert False
        else:
            schema = self.get_base_schema()
        assert issubclass(schema, Schema)
        return schema
    
    def get_object(self):
        if 'pk' in self.kwargs:
            return self.document.objects.get(pk=self.kwargs['pk'])
        return None

class CreateView(FragmentViewMixin, views.CreateView):
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        schema = self.get_schema()
        obj = self.get_active_object()
        if self.needs_typed_selection(schema, obj):
            return self.admin.get_select_schema_view()(request, *args, **kwargs)
        return super(CreateView, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = views.CreateView.get_context_data(self, **kwargs)
        context.update(FragmentViewMixin.get_context_data(self, **kwargs))
        opts = self.schema._meta
        context.update({'title': _('Add %s') % force_unicode(opts.verbose_name),
                        'show_delete': False,
                        'add': True,
                        'change': False,
                        'delete': False,
                        'adminform':self.create_admin_form(),})
        context['media'] += context['adminform'].form.media
        return context
    
    def form_valid(self, form):
        self.admin.log_addition(self.request, self.object)
        return FragmentViewMixin.form_valid(self, form)
    
class UpdateView(FragmentViewMixin, views.UpdateView):
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if not self.object:
            self.object = self.get_object()
        schema = self.get_schema()
        obj = self.get_active_object()
        if self.needs_typed_selection(schema, obj):
            return self.admin.get_select_schema_view(object=self.object)(request, *args, **kwargs)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = views.UpdateView.get_context_data(self, **kwargs)
        context.update(FragmentViewMixin.get_context_data(self, **kwargs))
        
        obj = self.object
        opts = self.schema._meta
        context.update({'title':_('Change %s') % force_unicode(opts.verbose_name),
                        'object_id': obj.get_id,
                        'original': obj,
                        'change': True,
                        'add': False,
                        'delete': False,
                        'adminform':self.create_admin_form(),})
        context['media'] += context['adminform'].form.media
        return context
    
    def form_valid(self, form):
        self.admin.log_change(self.request, self.object, '')
        return FragmentViewMixin.form_valid(self, form)

class DeleteView(DocumentViewMixin, views.DetailView):
    template_suffix = 'delete_selected_confirmation'
    title = _('Delete')
    key = 'delete'
    
    def get_context_data(self, **kwargs):
        context = views.DetailView.get_context_data(self, **kwargs)
        #context.update(FragmentViewMixin.get_context_data(self, **kwargs))
        #TODO add what will be deleted
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_repr = unicode(self.object)
        self.object.delete()
        self.admin.log_deletion(request, self.object, object_repr)
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_changelist'))

class HistoryView(DocumentViewMixin, views.ListView):
    title = _('History')
    key = 'history'

