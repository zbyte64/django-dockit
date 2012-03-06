from dockit.forms.widgets import PrimitiveListWidget

from django.conf import settings

class AdminPrimitiveListWidget(PrimitiveListWidget):
    class Media:
        css = {'all': ('%sadmin/css/primitivelist.css' % settings.STATIC_URL,)}
        js = ('%sadmin/js/primitivelist.js' % settings.STATIC_URL,)


