.. image:: https://secure.travis-ci.org/zbyte64/django-dockit.png?branch=master
   :target: http://travis-ci.org/zbyte64/django-dockit


Introduction
============

django-dockitcms provides a Document ORM in django. Dockitcms attempts to provide a batteries included experience while preserving django's various conventions.

--------
Features
--------

* Backendable support for document and index storage
 * Mongodb
 * Django Model with support for celery or ztask indexing
* Integrates with the django admin
 * Supports inlines
 * List Field support
 * Supports editing documents with deeply nested schemas
 * Robust design for customizing behavior on a per schema basis
* Class based views
* Django forms support
* Dynamically typed documents and schemas
* Document and Index routing to multiple backends


Installation
============

------------
Requirements
------------

* Python 2.6 or later
* Django 1.3 or later


--------
Settings
--------

Put 'dockit' into your ``INSTALLED_APPS`` section of your settings file.


Configuring Document Store Backend
----------------------------------

===============
Django Document
===============

Set the following in your settings file::

    DOCKIT_BACKENDS = {
        'default': {
            'ENGINE': 'dockit.backends.djangodocument.backend.ModelDocumentStorage',
        }
    }
    DOCKIT_INDEX_BACKENDS = {
        'default': {
            'ENGINE': 'dockit.backends.djangodocument.backend.ModelIndexStorage',
        },
    }

    #Uncomment to use django-ztask for indexing
    #DOCKIT_INDEX_BACKENDS['default']['INDEX_TASKS'] = 'dockit.backends.djangodocument.tasks.ZTaskIndexTasks'
    
    #Uncomment to use django-celery for indexing
    #DOCKIT_INDEX_BACKENDS['default']['INDEX_TASKS'] = 'dockit.backends.djangodocument.tasks.CeleryIndexTasks'

Then add 'dockit.backends.djangodocument' to ``INSTALLED_APPS``


=======
Mongodb
=======

Set the following in your settings file::

    DOCKIT_BACKENDS = {
        'default': {
            'ENGINE':'dockit.backends.mongo.backend.MongoDocumentStorage',
            'USER':'travis',
            'PASSWORD':'test',
            'DB':'mydb_test',
            'HOST':'127.0.0.1',
            'PORT':27017,
        }
    }
    DOCKIT_INDEX_BACKENDS = {
        'default': {
            'ENGINE':'dockit.backends.mongo.backend.MongoIndexStorage',
            'USER':'travis',
            'PASSWORD':'test',
            'DB':'mydb_test',
            'HOST':'127.0.0.1',
            'PORT':27017,
        },
    }

