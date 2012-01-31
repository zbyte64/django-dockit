from django import forms

class TypeSelectionForm(forms.Form):
    def __init__(self, schema, *args, **kwargs):
        super(TypeSelectionForm, self).__init__(*args, **kwargs)
        self.populate_type_field(schema)
    
    def populate_type_field(self, schema):
        doc_field = schema._meta.fields[schema._meta.typed_field]
        choices = doc_field.get_choices()
        self.fields[schema._meta.typed_field] = forms.ChoiceField(choices=choices)
