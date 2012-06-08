from django.contrib.admin.views.main import ChangeList as BaseChangeList, InvalidPage, IncorrectLookupParameters

class ChangeList(BaseChangeList):
    formset = None
    list_max_show_all = 200
    
    def get_query_set(self, request=None):
        return self.root_query_set
    
    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.query_set, self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        full_result_count = self.root_query_set.count()

        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            if isinstance(self.query_set, list):
                result_list = list(self.query_set)
            else:
                result_list = self.query_set._clone()
        else:
            try:
                result_list = paginator.page(self.page_num+1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

class ListFieldChangeList(ChangeList):
    def __init__(self, instance, dotpath, **kwargs):
        self.instance = instance
        self.dotpath = dotpath
        self.request = kwargs['request']
        super(ListFieldChangeList, self).__init__(**kwargs)
    
    def get_query_set(self, request=None):
        def _patch_instance(instance, index): #complete hack
            def serializable_value(*args):
                return index
            instance.serializable_value = serializable_value
            return instance
        return [_patch_instance(obj, index) for index, obj in enumerate(self.instance.dot_notation_to_value(self.dotpath) or [])]
    
    def url_for_result(self, result):
        dotpath = '%s.%s' % (self.dotpath, result.serializable_value())
        params = self.request.GET.copy()
        params['_dotpath'] = dotpath
        return "./?%s" % params.urlencode()

