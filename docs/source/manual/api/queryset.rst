Queryset
========

.. automodule:: dockit.backends.queryset


.. autoclass:: BaseDocumentQuery
    :members: __init__, document, backend, __len__, count, exists, delete, get, get_from_filter_operations, values, __getitem__, __nonzero__

.. autoclass:: QuerySet
    :members: __init__, document, __len__, count, delete, values, get, exists, __getitem__, __nonzero__, __iter__
