Schemas
=======

.. module:: dockit.schema.schema

The Schema Class
----------------

.. class:: Schema

    The :class:`~dockit.schema.schema.Schema` class provides a basic datatype
    for building up more complex Schemas and Documents. Schemas may embed other schemas.

    .. class method:: to_primitive(val)

        Returns a primitive representation of the schema that uses only built-in
        python structures and is json serializable
        

    .. class method:: to_python(val)

        Returns an instantiaded schema with the passed in value as the primitive data


The Document Class
------------------

.. class:: Document

    The :class:`~dockit.schema.schema.Document` class inherits from Schema
    and provides a persistant form of a schema.

    .. method:: save()

        Commit the document to the storage engine

    .. method:: delete()

        Remove this document from the storage engine

    .. property:: pk

        Returns the document identifier

The Document Manager
--------------------

.. class:: Manager

    The :class:`~dockit.schema.manager.Manager` class is assigned to the
    objects attribute of a document. The manager is used for retrieving
    documents.

    .. method:: all()

        Return all documents in the collection

    .. method:: get(**kwargs)

        Return the document matching the arguments

    .. method:: filter(**kwargs)

        An accessor for the filters.

    .. property:: values

        An accessor for the values.


