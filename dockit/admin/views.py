from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.utils.html import escape, escapejs
from django.contrib.admin import widgets, helpers
from django.conf.urls.defaults import url

from base import AdminViewMixin
from fields import EmbededSchemaField

from dockit import views
from dockit.forms import DocumentForm


class DocumentViewMixin(AdminViewMixin):
    template_suffix = None
    form_class = None
    
    @property
    def document(self):
        return self.admin.model
    
    def get_template_names(self):
        opts = self.document._meta
        app_label = opts.app_label
        object_name = opts.object_name.lower()
        return ['admin/%s/%s/%s.html' % (app_label, object_name, self.template_suffix),
                'admin/%s/%s.html' % (app_label, self.template_suffix),
                'admin/%s.html' % self.template_suffix]
    
    #def get_queryset(self):
    #    return self.model.objects.all()
    
    def get_context_data(self, **kwargs):
        opts = self.document._meta
        obj = None
        if hasattr(self, 'object'):
            obj = self.object
        context = AdminViewMixin.get_context_data(self, **kwargs)
        context.update({'root_path': self.admin_site.root_path,
                        'app_label': opts.app_label,
                        'opts': opts,
                        'module_name': force_unicode(opts.verbose_name_plural),
                        
                        'has_add_permission': self.admin.has_add_permission(self.request),
                        'has_change_permission': self.admin.has_change_permission(self.request, obj),
                        'has_delete_permission': self.admin.has_delete_permission(self.request, obj),
                        'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
                        'has_absolute_url': hasattr(self.document, 'get_absolute_url'),
                        #'content_type_id': ContentType.objects.get_for_model(self.model).id,
                        'save_as': self.admin.save_as,
                        'save_on_top': self.admin.save_on_top,})
        return context
    
    def create_admin_form(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        admin_form = helpers.AdminForm(form,
                                       list(self.admin.get_fieldsets(self.request)),
                                       self.admin.prepopulated_fields, 
                                       self.admin.get_readonly_fields(self.request),
                                       model_admin=self.admin)
        return admin_form
    
    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        if self.admin.form_class:
            return self.admin.form_class
        else:
            return self._generate_form_class()
    
    def _generate_form_class(self):
        if self.document is not None:
            # If a document has been explicitly provided, use it
            the_document = self.document
        elif hasattr(self, 'object') and self.object is not None:
            # If this view is operating on a single object, use
            # the class of that object
            the_document = self.object.__class__
        else:
            # Try to get a queryset and extract the document class
            # from that
            the_document = self.get_queryset().document
        #fields = fields_for_document(document)
        class CustomDocumentForm(DocumentForm):
            class Meta:
                document = the_document
                form_field_callback = self.admin.formfield_for_field
        #CustomDocumentForm.base_fields.update(fields)
        return CustomDocumentForm

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

#the big and ugly callback
CALL_BACK = '''
<script type="text/javascript">
parent.dismissFragmentPopup(window, "%(value)s", "%(name)s");
</script>
'''

class CreateView(DocumentViewMixin, views.CreateView):
    template_suffix = 'change_form'
    
    def get_context_data(self, **kwargs):
        context = views.CreateView.get_context_data(self, **kwargs)
        context.update(DocumentViewMixin.get_context_data(self, **kwargs))
        opts = self.document._meta
        context.update({'title': _('Add %s') % force_unicode(opts.verbose_name),
                        'show_delete': False,
                        'add': True,
                        'change': False,
                        'delete': False,
                        'adminform':self.create_admin_form(),})
        context['media'] += context['adminform'].form.media
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        self.admin.log_addition(self.request, self.object)
        if "_popup" in self.request.POST:
            return HttpResponse(CALL_BACK % \
                # escape() calls force_unicode.
                {'value': escape(self.object.get_id()), 
                 'name': escapejs(self.document._meta.verbose_name)})
        if '_continue' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_change', self.object.get_id()))
        if '_addanother' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_add'))
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_index'))
    
class UpdateView(DocumentViewMixin, views.UpdateView):
    template_suffix = 'change_form'
    
    def get_object(self):
        if not hasattr(self, 'object'):
            self.object = views.UpdateView.get_object(self)
        return self.object
    
    def get_context_data(self, **kwargs):
        context = views.UpdateView.get_context_data(self, **kwargs)
        context.update(DocumentViewMixin.get_context_data(self, **kwargs))
        
        obj = self.get_object()
        opts = self.document._meta
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
        self.object = form.save()
        self.admin.log_change(self.request, self.object, '')
        if '_continue' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_change', self.object.get_id()))
        if '_addanother' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_add'))
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_index'))

class DeleteView(DocumentViewMixin, views.DetailView):
    template_suffix = 'delete_selected_confirmation'
    title = _('Delete')
    key = 'delete'
    
    def get_context_data(self, **kwargs):
        context = views.DetailView.get_context_data(self, **kwargs)
        context.update(DocumentViewMixin.get_context_data(self, **kwargs))
        #TODO add what will be deleted
        return context
    
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        object_repr = unicode(obj)
        obj.delete()
        self.admin.log_deletion(request, obj, object_repr)
        return HttpResponseRedirect(self.admin.reverse('index'))

class HistoryView(DocumentViewMixin, views.ListView):
    title = _('History')
    key = 'history'

from django.utils import simplejson
from django.http import HttpResponse
from django.views.generic import TemplateView

from dockit.models import SchemaFragment
from dockit.backends import get_document_backend


class SchemaFieldView(DocumentViewMixin, TemplateView):
    """
    Get params:
    None - creates a new fragment
    ?fragment=<fragment_id> - edits a fragment that already exists
    ?collection=<collection>&docid=<docid>&dotpath=<dotpath> - loads an existing portion of a document into a fragment
    
    Always returns the fragment id associated to the edit
    """
    template_suffix = 'schema_form'
    uri = None
    document = None
    
    def load_fragment_data(self):
        backend = get_document_backend()
        doc = backend.get(self.request.GET['collection'], self.request.GET['docid'])
        data = doc.dotpath(self.request.GET['dotpath'])
        return data
    
    def create_admin_form(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        admin_form = helpers.AdminForm(form,
                                       [(None, {'fields': form.fields.keys()})],
                                       {},#self.admin.prepopulated_fields, 
                                       [],#self.admin.get_readonly_fields(self.request),
                                       model_admin=self.admin)
        return admin_form
    
    def get_form_kwargs(self):
        kwargs = dict()
        storage = self.get_fragment_store()
        if storage.data:
            kwargs['initial'] = storage.data
        if self.request.POST:
            kwargs.update({'files':self.request.FILES,
                           'data': self.request.POST,})
        return kwargs
    
    def get_form_class(self):
        if self.form_class:
            return self.form_class
        return self._generate_form_class()
    
    def get_form(self, form_class):
        return form_class(**self.get_form_kwargs())
    
    def get_context_data(self, **kwargs):
        context = DocumentViewMixin.get_context_data(self, **kwargs)
        context.update(DocumentViewMixin.get_context_data(self, **kwargs))
        opts = self.document._meta
        context.update({'title': _('Add %s') % force_unicode(opts.verbose_name),
                        'show_delete': False,
                        'add': True,
                        'change': False,
                        'delete': False,
                        'adminform':self.create_admin_form(),})
        context['media'] += context['adminform'].form.media
        return context
    
    def get_identifier(self):
        cls = type(self)
        return '%s.%s' % (cls.__module__, cls.__name__)
    
    def get_fragment_store(self):
        if 'fragment' in self.request.GET:
            storage = SchemaFragment.objects.get(self.request.GET['fragment'])
        else:
            storage = SchemaFragment(identifier=self.get_identifier())
        if 'docid' in self.request.GET and 'collection' in self.request.GET and 'dotpath' in self.request.GET:
            storage.data = self.load_fragment_data()
        return storage
    
    def form_valid(self, form):
        storage = self.get_fragment_store()
        storage.data = form.cleaned_data
        storage.save()
        if "_popup" in self.request.POST or True:
            return HttpResponse(CALL_BACK % \
                # escape() calls force_unicode.
                {'value': escape(storage.get_id()), 
                 'name': escapejs(self.document._meta.verbose_name)})
        return HttpResponse(simplejson.dumps(storage.pk))
    
    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            return self.form_valid(form)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    @classmethod
    def get_field(cls):
        return EmbededSchemaField(view=cls())
    
    @classmethod
    def get_url_line(cls, admin):
        name = cls.uri.rsplit(':', 1)[-1]
        key = name.rsplit('_', 1)[-1]
        return url(key+'/$', cls.as_view(**{'admin':admin, 'admin_site':admin.admin_site}), name=name)

class SchemaListFieldView(SchemaFieldView):
    pass #TODO

class FragmentViewMixin(AdminViewMixin):
    template_suffix = 'change_form'
    
    form_class = None
    schema = None
    document = None
    
    def get_template_names(self):
        opts = self.document._meta
        app_label = opts.app_label
        object_name = opts.object_name.lower()
        return ['admin/%s/%s/%s.html' % (app_label, object_name, self.template_suffix),
                'admin/%s/%s.html' % (app_label, self.template_suffix),
                'admin/%s.html' % self.template_suffix]
    
    #def get_queryset(self):
    #    return self.model.objects.all()
    
    def create_admin_form(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        admin_form = helpers.AdminForm(form,
                                       list(self.admin.get_fieldsets(self.request)),
                                       self.admin.prepopulated_fields, 
                                       self.admin.get_readonly_fields(self.request),
                                       model_admin=self.admin)
        return admin_form
    
    def get_context_data(self, **kwargs):
        context = AdminViewMixin.get_context_data(self, **kwargs)
        opts = self.document._meta
        context.update({'title': _('Add %s') % force_unicode(opts.verbose_name),
                        'show_delete': False,
                        'add': True,
                        'change': False,
                        'delete': False,
                        'adminform':self.create_admin_form(),})
        context['media'] += context['adminform'].form.media
        
        obj = None
        if hasattr(self, 'object'):
            obj = self.object
        
        context.update({'root_path': self.admin_site.root_path,
                        'app_label': opts.app_label,
                        'opts': opts,
                        'module_name': force_unicode(opts.verbose_name_plural),
                        
                        'has_add_permission': self.admin.has_add_permission(self.request),
                        'has_change_permission': self.admin.has_change_permission(self.request, obj),
                        'has_delete_permission': self.admin.has_delete_permission(self.request, obj),
                        'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
                        'has_absolute_url': hasattr(self.document, 'get_absolute_url'),
                        #'content_type_id': ContentType.objects.get_for_model(self.model).id,
                        'save_as': self.admin.save_as,
                        'save_on_top': self.admin.save_on_top,})
        
        return context
    
    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        else:
            return self._generate_form_class()
    
    def _generate_form_class(self):
        class CustomDocumentForm(DocumentForm):
            class Meta:
                document = self.schema
                form_field_callback = self.admin.formfield_for_field
        #CustomDocumentForm.base_fields.update(fields)
        return CustomDocumentForm
    
    def load_fragment_data(self):
        doc = self.document.objects.get(self.kwargs['pk']) #TODO get_object instead
        data = doc.dotpath(self.request.GET['dotpath'])
        return data
    
    def get_fragment_store(self):
        if 'fragment' in self.request.GET:
            storage = SchemaFragment.objects.get(self.request.GET['fragment'])
        else:
            storage = SchemaFragment()
        if 'pk' in self.kwargs and 'dotpath' in self.request.GET:
            storage.data = self.load_fragment_data()
        return storage
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if not self.form.is_valid():
            return self.form_invalid(form)
        for key in request.POST.iterkeys():
            if key.startswith('fragment[') and key.endswith(']'): #submitted, but wants to drill into a fragment
                fieldname = key.split('[', 1)[1].rsplit(']', 1)[0]
                fragment = self.get_fragment_store()
                fragment.data = form.cleaned_data
                fragment.save()
                # type(self).as_view(document=schema).get_form...
                #TODO store fragment, redirect view that handles this view
                #?dotpath=<dotpathsofar>.<fieldname>&parent_fragment=storage.get_id(),
                #TODO schemaforms should take a dotpath argument, saves and loads relative to the dotpath
        #CONSIDER: if parent_fragment, merge with parent fragment, redirect to view of parent
        return self.form_valid(form)
    
    def form_valid(self, form):
        form.cleaned_data
        #TODO merge cleaned_data with parent_fragment
        if "_popup" in self.request.POST:
            return HttpResponse(CALL_BACK % \
                # escape() calls force_unicode.
                {'value': escape(self.object.get_id()), 
                 'name': escapejs(self.document._meta.verbose_name)})
        if '_continue' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_change', self.object.get_id()))
        if '_addanother' in self.request.POST:
            return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_add'))
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_index'))

def store_fragment(form):
    document = form._meta.document
    for fieldname in form._meta.fields.iterkeys():
        val = form._raw_value(fieldname)
        if fieldname in document._meta.fields:
            val = document._meta.fields[fieldname].to_primitive(val)

