from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.views.generic import detail as detailview
from django.utils.translation import ugettext as _
from django.http import Http404

class SingleObjectMixin(detailview.SingleObjectMixin):
    document = None
    
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()
        
        pk = self.kwargs.get('pk', None)
        slug = self.kwargs.get('slug', None)
        try:
            if pk is not None:
                return queryset.get(pk=self.kwargs['pk'])
            elif slug is not None:
                slug_field = self.get_slug_field()
                return queryset.get(**{slug_field:self.kwargs['slug']})
            
        except (ObjectDoesNotExist, IndexError):
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.document._meta.verbose_name})
    
    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.document is not None:
            queryset = self.document.objects
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'document'"
                                       % self.__class__.__name__)
        return queryset

class BaseDetailView(SingleObjectMixin, detailview.BaseDetailView):
    pass

class DetailView(BaseDetailView, detailview.SingleObjectTemplateResponseMixin):
    pass

class SingleObjectTemplateResponseMixin(SingleObjectMixin, detailview.SingleObjectTemplateResponseMixin):
    pass
