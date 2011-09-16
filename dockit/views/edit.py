from django.core.exceptions import ImproperlyConfigured
from django.views.generic import edit as editview

from detail import SingleObjectMixin, SingleObjectTemplateResponseMixin, BaseDetailView

from dockit.forms import DocumentForm

class DocumentFormMixin(editview.FormMixin, SingleObjectMixin):
    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        else:
            if self.document is not None:
                # If a document has been explicitly provided, use it
                document = self.document
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                document = self.object.__class__
            else:
                # Try to get a queryset and extract the document class
                # from that
                document = self.get_queryset().document
            #fields = fields_for_document(document)
            class CustomDocumentForm(DocumentForm):
                class Meta:
                    document = document
            #CustomDocumentForm.base_fields.update(fields)
            return CustomDocumentForm

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(DocumentFormMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.object})
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the document.")
        return url

    def form_valid(self, form):
        self.object = form.save()
        return super(DocumentFormMixin, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = kwargs
        if getattr(self, 'object', None):
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        return context

class BaseCreateView(DocumentFormMixin, editview.ProcessFormView):
    """
    Base view for creating an new object instance.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).post(request, *args, **kwargs)


class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
    """
    View for creating an new object instance,
    with a response rendered by template.
    """
    template_name_suffix = '_form'


class BaseUpdateView(DocumentFormMixin, editview.ProcessFormView):
    """
    Base view for updating an existing object.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class UpdateView(SingleObjectTemplateResponseMixin, BaseUpdateView):
    """
    View for updating an object,
    with a response rendered by template..
    """
    template_name_suffix = '_form'

DeletionMixin = editview.DeletionMixin

class BaseDeleteView(DeletionMixin, BaseDetailView):
    """
    Base view for deleting an object.

    Using this base class requires subclassing to provide a response mixin.
    """


class DeleteView(SingleObjectTemplateResponseMixin, BaseDeleteView):
    """
    View for deleting an object retrieved with `self.get_object()`,
    with a response rendered by template.
    """
    template_name_suffix = '_confirm_delete'

