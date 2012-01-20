from fields import BaseField as Field

from django.db.models.fields.files import FieldFile, FileDescriptor
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext_lazy
from django.core.files.storage import default_storage
from django.core.files import File
from django import forms

import datetime
import os

class FileField(Field):
    # The class to wrap instance attributes in. Accessing the file object off
    # the instance will always return an instance of attr_class.
    attr_class = FieldFile

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = FileDescriptor

    description = ugettext_lazy("File path")
    
    form_field_class = forms.FileField

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to

        super(FileField, self).__init__(verbose_name, name, **kwargs)

    def get_internal_type(self):
        return "FileField"

    #def contribute_to_class(self, cls, name):
    #    super(FileField, self).contribute_to_class(cls, name)
    #    setattr(cls, self.name, self.descriptor_class(self))

    def get_directory_name(self):
        return os.path.normpath(force_unicode(datetime.datetime.now().strftime(smart_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))

    def formfield(self, **kwargs):
        # If a file has been provided previously, then the form doesn't require
        # that a new file is provided this time.
        # The code to mark the form field as not required is used by
        # form_for_instance, but can probably be removed once form_for_instance
        # is gone. ModelForm uses a different method to check for an existing file.
        if 'initial' in kwargs:
            kwargs['required'] = False
        return super(FileField, self).formfield(**kwargs)
    
    def is_instance(self, val):
        return isinstance(val, File)
    
    def to_primitive(self, val):
        """
        Takes a python object and returns an object that is [json] serializable
        """
        if not val:
            return None
        if isinstance(val, basestring):
            return val
        if getattr(val, 'storage_path', False):
            return val.storage_path
        name = self.generate_filename(val.name)
        name = self.storage.save(name, val)
        assert name
        return name
    
    def to_python(self, val, parent=None):
        if not val:
            return None
        #self.attr_class(instance, field, name)
        ret = self.storage.open(val)
        ret.storage_path = val
        try:
            ret.url = self.storage.url(val)
        except Exception, error:
            print error
        return ret

