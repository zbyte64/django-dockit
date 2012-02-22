from django.core.urlresolvers import reverse

class Breadcrumb(object):
    def __init__(self, name, url=None):
        self.name = name
        self.url = url
    
    def get_absolute_url(self):
        if not isinstance(self.url, basestring):
            return reverse(*self.url)
        return self.url

