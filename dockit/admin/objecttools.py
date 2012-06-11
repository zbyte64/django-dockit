from django.template.loader import get_template
from django.template import Context

class ObjectTool(object):
    def render(self, request, context):
        pass

class LinkObjectTool(object):
    template_name = 'admin/object_tool.html'
    
    def __init__(self, title, url, css_class=''):
        self.title = title
        self.url = url
        self.css_class = css_class
    
    def render(self, request, context):
        template = get_template(self.template_name)
        context = Context({'title':self.title,
                           'url':self.url,
                           'css_class':self.css_class,})
        return template.render(context)

