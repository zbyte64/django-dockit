from dockit.forms.widgets import PrimitiveListWidget

class AdminPrimitiveListWidget(PrimitiveListWidget):
    class Media:
        js = ('/static/admin/js/primitivelist.js',)


