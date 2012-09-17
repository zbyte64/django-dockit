from dockit.views.detail import SingleObjectMixin

from hyperadmin.resources.crud.views import CRUDDetailMixin, CRUDCreateView, CRUDListView, CRUDDeleteView, CRUDDetailView

class DocumentMixin(object):
    document = None
    queryset = None
    
    def get_queryset(self):
        return self.resource.get_queryset(self.request.user)
    
    def get_changelist(self):
        if not hasattr(self, '_changelist'):
            self._changelist = self.resource.get_changelist(self.request.user, self.request.GET)
        return self._changelist

class DocumentCreateView(DocumentMixin, CRUDCreateView):
    pass

class DocumentListView(DocumentMixin, CRUDListView):
    def get_state(self):
        state = super(DocumentListView, self).get_state()
        state['changelist'] = self.get_changelist()
        return state
    
    def get_paginator(self):
        return self.get_changelist().paginator

class DocumentDetailMixin(DocumentMixin, CRUDDetailMixin, SingleObjectMixin):
    def get_object(self):
        if not hasattr(self, 'object'):
            self.object = SingleObjectMixin.get_object(self)
        return self.object

class DocumentDeleteView(DocumentDetailMixin, CRUDDeleteView):
    pass

class DocumentDetailView(DocumentDetailMixin, CRUDDetailView):
    pass

