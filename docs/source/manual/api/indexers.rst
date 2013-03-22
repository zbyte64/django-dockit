Indexers
========

The Base Indexer Class
----------------------

.. class:: BaseIndexer

    The :class:`~dockit.backends.indexer.BaseIndexer` class provides is an abstract class
    whose implementation provides querying functionality. An indexer is instantiated with
    the document, name and params.

    .. class method:: filter()

        Returns a set of documents matching the filter criteria
        

    .. class method:: values()

        Returns a set of values from the documents matching the filter criteria

    .. class method:: on_document_save(instance)

        Called when a document is saved

    .. class method:: on_document_delete(instance)

        Called when a dcoument is deleted


