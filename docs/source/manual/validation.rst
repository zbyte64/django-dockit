==========
Validation
==========

Documents and Schemas support validation that mimics Django's models. Given a document instance you may call `full_clean` to validate the document structure and have a `ValidationError` raised if the document does not conform. Documents and schemas may define their own `clean_<fieldname>` method to validate each entry and a `clean` method to validate the entire document. All validation errors are to be sublcassed from `django.core.exceptions.ValidationError`.


To run through the document validation run `full_clean`::

    try:
        mydocument.full_clean()
    except ValidationError as e:
        print e
        raise

Adding custom validation to a document::

    class MyDocument(schema.Document):
        full_name = schema.CharField()
        
        def clean_full_name(self):
            value = self.full_name.strip()
            if ' ' not full_name:
                raise ValidationError('A full name must have a first and last name')
            return full_name.strip()
        
        def clean(self):
            if datetime.date.today().weekday() == 2:
                raise ValidationError('You cannot validate on a Wednesday!')
