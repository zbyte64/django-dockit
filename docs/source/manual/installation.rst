Installation
============

------------
Requirements
------------

* Python 2.5 or later
* Django 1.3


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

    DOCKIT_BACKEND = 'dockit.backends.djangodocument.backend.ModelDocumentStorage'


=======
Mongodb
=======

Set the following in your settings file::

    DOCKIT_BACKEND = 'dockit.backends.mongo.backend.MongoDocumentStorage'
    MONGO_HOST = '127.0.0.1
    MONGO_PORT = 27017
    MONGO_USER = ''
    MONGO_PASSWORD = ''
    MONGO_DB = ''

Note: the configuration parameters are likely to change in the future.

