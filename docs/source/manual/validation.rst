==========
Validation
==========

Documents and Schemas support validation that mimics Django's models. Given a document instance you may call `full_clean` to validate the document structure and have a `ValidationError` raised if the document does not conform. Documents and schemas may define their own `clean_<fieldname>` method to validate each entry.
