from django.conf.urls.defaults import patterns, url, include
from django.utils.functional import update_wrapper

from hyperadmin.hyperobjects import Link
from hyperadmin.resources.crud.crud import CRUDResource

from dockit import forms
from dockit.paginator import Paginator
from dockit.resources import views
from dockit.resources.changelist import ChangeList


class DocumentResource(CRUDResource):
    #TODO support the following:
    #raw_id_fields = ()
    fields = None
    exclude = []
    #fieldsets = None
    #filter_vertical = ()
    #filter_horizontal = ()
    #radio_fields = {}
    #prepopulated_fields = {}
    formfield_overrides = {}
    #readonly_fields = ()
    #declared_fieldsets = None
    
    #save_as = False
    #save_on_top = False
    changelist = ChangeList
    paginator = Paginator
    
    #list display options
    list_display_links = ()
    list_filter = ()
    list_select_related = False
    list_per_page = 100
    list_max_show_all = 200
    list_editable = ()
    search_fields = ()
    date_hierarchy = None
    ordering = None
    
    list_view = views.DocumentListView
    add_view = views.DocumentCreateView
    detail_view = views.DocumentDetailView
    delete_view = views.DocumentDeleteView
    
    def __init__(self, *args, **kwargs):
        super(DocumentResource, self).__init__(*args, **kwargs)
        self.document = self.resource_adaptor
    
    @property
    def opts(self):
        return self.resource_adaptor._meta
    
    def get_app_name(self):
        return self.opts.app_label
    app_name = property(get_app_name)
    
    def get_resource_name(self):
        return self.opts.module_name
    resource_name = property(get_resource_name)
    
    def get_prompt(self):
        return self.resource_name
    
    def get_view_kwargs(self):
        kwargs = super(DocumentResource, self).get_view_kwargs()
        kwargs['document'] = self.resource_adaptor
        return kwargs
    
    def get_instances(self, state):
        if 'changelist' in state:
            return state['changelist'].result_list
        return super(DocumentResource, self).get_instances(state) #TODO power by get_queryset
    
    def get_changelist(self, user, filter_params=None):
        changelist_cls = self.changelist
        kwargs = {'document':self.resource_adaptor,
                  'root_query_set': self.get_queryset(user),
                  'user':user,
                  'filter_params':filter_params or dict(),
                  'list_display':self.list_display,
                  'list_display_links':self.list_display_links,
                  'list_filter':self.list_filter,
                  'date_hierarchy':self.date_hierarchy,
                  'search_fields':self.search_fields,
                  'list_select_related':self.list_select_related,
                  'list_per_page':self.list_per_page,
                  'list_max_show_all':self.list_max_show_all,
                  'list_editable':self.list_editable,
                  'resource':self,}
        return changelist_cls(**kwargs)
    
    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return self.paginator(queryset, per_page, orphans, allow_empty_first_page)
    
    def get_templated_queries(self, state):
        links = super(DocumentResource, self).get_templated_queries(state)
        if state and 'changelist' in state:
            links += self.get_changelist_links(state)
        return links
    
    def get_changelist_links(self, state):
        links = self.get_changelist_sort_links(state)
        links += self.get_changelist_filter_links(state)
        links += self.get_pagination_links(state)
        #links.append(self.get_search_link())
        return links
    
    def get_changelist_sort_links(self, state):
        links = list()
        changelist = state['changelist']
        from django.contrib.admin.templatetags.admin_list import result_headers
        for header in result_headers(changelist):
            if header.get("sortable", False):
                prompt = unicode(header["text"])
                classes = ["sortby"]
                if "url" in header:
                    links.append(self.get_resource_link(url=header["url"], prompt=prompt, classes=classes+["primary"], rel="sortby"))
                else:
                    if header["ascending"]:
                        classes.append("ascending")
                    if header["sorted"]:
                        classes.append("sorted")
                    links.append(self.get_resource_link(url=header["url_primary"], prompt=prompt, classes=classes+["primary"], rel="sortby"))
                    links.append(self.get_resource_link(url=header["url_remove"], prompt=prompt, classes=classes+["remove"], rel="sortby"))
                    links.append(self.get_resource_link(url=header["url_toggle"], prompt=prompt, classes=classes+["toggle"], rel="sortby"))
        return links
    
    def get_changelist_filter_links(self, state):
        links = list()
        changelist = state['changelist']
        for spec in changelist.filter_specs:
            choices = spec.choices(changelist)
            for choice in choices:
                classes = ["filter"]
                if choice['selected']:
                    classes.append("selected")
                title = spec.title
                if callable(title):
                    title = title()
                prompt = u"%s: %s" % (title, choice['display'])
                links.append(self.get_resource_link(url=choice['query_string'], prompt=prompt, classes=classes, rel="filter"))
        return links
    
    def get_search_link(self, state):
        pass
    
    def get_pagination_links(self, state):
        links = list()
        changelist = state['changelist']
        paginator, page_num = changelist.paginator, changelist.page_num
        from django.contrib.admin.templatetags.admin_list import pagination
        from django.contrib.admin.views.main import PAGE_VAR
        ctx = pagination(changelist)
        classes = ["pagination"]
        for page in ctx["page_range"]:
            if page == '.':
                continue
            url = changelist.get_query_string({PAGE_VAR: page})
            links.append(self.get_resource_link(url=url, prompt=u"%s" % page, classes=classes, rel="pagination"))
        if ctx["show_all_url"]:
            links.append(self.get_resource_link(url=ctx["show_all_url"], prompt="show all", classes=classes, rel="pagination"))
        return links
    
    def lookup_allowed(self, lookup, value):
        return True #TODO
    
    def get_ordering(self):
        """
        Hook for specifying field ordering.
        """
        return self.ordering or ()  # otherwise we might try to *None, which is bad ;)
    
    def get_queryset(self, user):
        queryset = self.resource_adaptor.objects.all()
        if not self.has_change_permission(user):
            queryset = queryset.none()
        return queryset

    def has_add_permission(self, user):
        if self.opts.auto_created:
            # We're checking the rights to an auto-created intermediate Document,
            # which doesn't have its own individual permissions. The user needs
            # to have the change permission for the related Document in order to
            # be able to do anything with the intermediate Document.
            return self.has_change_permission(user)
        return user.has_perm(
            self.opts.app_label + '.' + self.opts.get_add_permission())

    def has_change_permission(self, user, obj=None):
        opts = self.opts
        if opts.auto_created and hasattr(self, 'parent_document'):
            # The Document was auto-created as intermediary for a
            # ManyToMany-relationship, find the target Document
            for field in opts.fields:
                if field.rel and field.rel.to != self.parent_Document:
                    opts = field.rel.to._meta
                    break
        return user.has_perm(
            opts.app_label + '.' + opts.get_change_permission())

    def has_delete_permission(self, user, obj=None):
        if self.opts.auto_created:
            # We're checking the rights to an auto-created intermediate Document,
            # which doesn't have its own individual permissions. The user needs
            # to have the change permission for the related Document in order to
            # be able to do anything with the intermediate Document.
            return self.has_change_permission(user, obj)
        return user.has_perm(
            self.opts.app_label + '.' + self.opts.get_delete_permission())
    
    def get_form_class(self):
        if self.form_class:
            return self.form_class
        class AdminForm(forms.DocumentForm):
            class Meta:
                document = self.document
                exclude = self.exclude
                #TODO formfield overides
                #TODO fields
        return AdminForm

