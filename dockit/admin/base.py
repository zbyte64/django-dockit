
class AdminViewMixin:
    admin = None
    admin_site = None
    
    def is_popup(self):
        return "_popup" in self.request.REQUEST
    
    def get_context_data(self, **kwargs):
        return {'media': self.admin.media,
                'admin': self.admin,
                'admin_site': self.admin_site,
                'is_popup': self.is_popup()}


