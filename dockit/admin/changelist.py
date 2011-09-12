from django.contrib.admin.views.main import ChangeList as BaseChangeList, MAX_SHOW_ALL_ALLOWED, InvalidPage, IncorrectLookupParameters

class ChangeList(BaseChangeList):
    formset = None
    
    def get_query_set(self):
        return self.root_query_set
    
    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.query_set, self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count
        
        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        full_result_count = result_count
        
        can_show_all = result_count <= MAX_SHOW_ALL_ALLOWED
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.query_set
        else:
            try:
                result_list = paginator.page(self.page_num+1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.full_result_count = full_result_count
        if callable(result_list):
            result_list = result_list()
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

