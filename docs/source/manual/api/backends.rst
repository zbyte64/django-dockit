Backends
========

.. automodule:: dockit.backends

------------
Base Backend
------------

.. automodule:: dockit.backends.base

.. autoclass:: BaseDocumentQuerySet
    :members: __len__, count, delete, all, get, __getitem__, __nonzero__

.. autoclass:: BaseDocumentStorage
    :members:

.. autoclass:: BaseIndexStorage
    :members:

----------------
Builtin Backends
----------------

Mongo Backend
-------------

.. automodule:: dockit.backends.mongo

TODO

Django Document Backend
-----------------------

.. automodule:: dockit.backends.djangodocument

.. automodule:: dockit.backends.djangodocument.backend

.. autoclass:: DocumentQuery
    :show-inheritance:
    :members:

.. autoclass:: IndexedDocumentQuery
    :show-inheritance:
    :members:

.. autoclass:: ModelIndexStorage
    :show-inheritance:
    :members:

.. autoclass:: ModelDocumentStorage
    :show-inheritance:
    :members:
