from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.utils.html import escape, escapejs
from django.contrib.admin import widgets, helpers
from django.conf.urls.defaults import url

from base import AdminViewMixin
from fields import DotPathField

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

from dockit.models import TemporaryDocument
from dockit.backends import get_document_backend

from urllib import urlencode

class FragmentViewMixin(AdminViewMixin):
    template_suffix = 'change_form'
    
    form_class = None
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
    
    def dotpath(self):
        return self.request.GET.get('dotpath', None)
    
    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class and not self.dotpath():
            return self.form_class
        else:
            return self._generate_form_class(self.document)
    
    def _generate_form_class(self, schema):
        class CustomDocumentForm(DocumentForm):
            class Meta:
                document = schema
                form_field_callback = self.admin.formfield_for_field
                dotpath = self.dothpath() or None
        return CustomDocumentForm
    
    def load_fragment_data(self):
        doc = self.get_object()
        data = doc.dot_notation(self.dotpath())
        return data
    
    def get_fragment_store(self):
        #TODO cache this
        if 'fragment' in self.request.GET:
            storage = TemporaryDocument.objects.get(self.request.GET['fragment'])
        else:
            storage = TemporaryDocument()
            if 'pk' in self.kwargs:
                storage.data = self.get_object()
        return storage
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if not self.form.is_valid():
            return self.form_invalid(form)
        
        obj = form.save() #CONSIDER this would normally be done in form_valid
        if not self.dotpath():
            self.object = obj
        
        for key in request.POST.iterkeys():
            if key.startswith('fragment[') and key.endswith(']'): #submitted, but wants to drill into a fragment
                fieldname = key.split('[', 1)[1].rsplit(']', 1)[0]
                fragment = self.get_fragment_store()
                params = {'dotpath':'%s.%s' % (self.dotpath(), fieldname),
                          'fragment':fragment.get_id(),}
                return HttpResponseRedirect('%s?%s' % (request.path, urlencode(params)))
        if self.dotpath():
            fragment = self.get_fragment_store()
            params = {'fragment':fragment.get_id(),}
            dotpath = self.dotpath()
            dotpath = dotpath[:dopath.rfind('.')]
            if dotpath:
                params['dotpath'] = dotpath
            return HttpResponseRedirect('%s?%s' % (request.path, urlencode(params)))
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
        return HttpResponseRedirect(self.admin.reverse(self.admin.app_name+'_index'))

def store_fragment(form):
    document = form._meta.document
    for fieldname in form._meta.fields.iterkeys():
        val = form._raw_value(fieldname)
        if fieldname in document._meta.fields:
            val = document._meta.fields[fieldname].to_primitive(val)

