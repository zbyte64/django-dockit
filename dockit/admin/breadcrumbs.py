from django.core.urlresolvers import reverse

class Breadcrumb(object):
    def __init__(self, name, url=None):
        self.name = name
        self.url = url
    
    def get_absolute_url(self):
        if not isinstance(self.url, basestring):
            if len(self.url) > 1: #hack
                return reverse(self.url[0], args=self.url[1], kwargs=self.url[2])
            return reverse(*self.url)
        return self.url

