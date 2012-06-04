Backends
========

.. module:: dockit.backends

------------
Base Backend
------------

.. class:: BaseDocumentQuerySet

    The :class:`~dockit.backends.base.BaseDocumentQuerySet` class provides an interface
    for implementing document querysets.

    .. method:: __len__()

        returns an integer representing the number of items in the queryset
        

    .. method:: delete()

        deletes all the documents in the given queryset

    .. method:: get(doc_id)

        returns the documents with the given id belonging to the queryset

    .. method:: __getitem__(val)

        returns a document or a slice of documents

    .. method:: __nonzero__

        returns True if the queryset is not empty

    .. method:: __and__(other)

        TODO

    .. method:: __or__(other)

        TODO

.. class:: BaseDocumentStorage

    The :class:`~dockit.backends.base.BaseDocumentStorage` class provides an interface
    for implementing document storage backends.

    .. method:: get_query(query_index)

        return an implemented `BaseDocumentQuerySet` that contains all the documents

    .. method:: register_document(document)

        is called for every document registered in the system

    .. method:: save(doc_class, collection, data)

        stores the given primitive data in the specified collection

    .. method:: get(doc_class, collection, doc_id)

        returns the primitive data for the document belonging in the specified collection

    .. method:: delete(doc_class, collection, doc_id)

        deletes the given document from the specified collection

    .. method:: get_id_field_name()

        returns a string representing the primary key field name

.. class:: BaseIndexStorage

    The :class:`~dockit.backends.base.BaseIndexStorage` class provides an interface
    for implementing index storage backends.

    .. method:: register_index(self, query_index)

        TODO

    .. method:: get_query(query_index)

        returns an implemented `BaseDocumentQuerySet` representing the query index
        

    .. method:: register_document(document)

        TODO

    .. method:: save(doc_class, collection, data)

        is called for every document save

    .. method:: delete(doc_class, collection, doc_id)

        is called for every document delete


Mongo Backend
-------------

TODO

Django Document Backend
-----------------------

Recommended for dev and testing purposes only.
