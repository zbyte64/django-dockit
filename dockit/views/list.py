from dockit.paginator import Paginator

from django.core.exceptions import ImproperlyConfigured
from django.views.generic import list as listview

class MultipleObjectMixin(listview.MultipleObjectMixin):
    paginator_class = Paginator
    document = None
    
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
            queryset = self.document.objects.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset

class BaseListView(MultipleObjectMixin, listview.BaseListView):
    pass

class ListView(listview.MultipleObjectTemplateResponseMixin, BaseListView):
    pass
