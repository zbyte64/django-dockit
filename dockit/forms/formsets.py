from django.forms.formsets import BaseFormSet, formset_factory
from django.utils.text import get_text_list, capfirst
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from forms import DocumentForm, documentform_factory

class BaseDocumentFormSet(BaseFormSet):
    """
    A ``FormSet`` for editing a queryset and/or adding new objects to it.
    """
    document = None

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 queryset=None, **kwargs):
        self.queryset = queryset
        defaults = {'data': data, 'files': files, 'auto_id': auto_id, 'prefix': prefix}
        defaults.update(kwargs)
        super(BaseDocumentFormSet, self).__init__(**defaults)

    def initial_form_count(self):
        """Returns the number of forms that are required in this FormSet."""
        if not (self.data or self.files):
            return len(self.get_queryset())
        return super(BaseDocumentFormSet, self).initial_form_count()

    def _existing_object(self, pk):
        if not hasattr(self, '_object_dict'):
            self._object_dict = dict([(i, o) for i, o in enumerate(self.get_queryset())])
        return self._object_dict.get(pk)

    def _construct_form(self, i, **kwargs):
        if self.is_bound and i < self.initial_form_count():
            # Import goes here instead of module-level because importing
            # django.db has side effects.
            
            kwargs['instance'] = self._existing_object(i)
        if i < self.initial_form_count() and not kwargs.get('instance'):
            kwargs['instance'] = self.get_queryset()[i]
        return super(BaseDocumentFormSet, self)._construct_form(i, **kwargs)

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            if self.queryset is not None:
                qs = self.queryset
            else:
                qs = self.document.objects.all()

            # If the queryset isn't already ordered we need to add an
            # artificial ordering here to make sure that all formsets
            # constructed from this queryset have the same form order.
            #if not qs.ordered:
            #    qs = qs.order_by(self.model._meta.pk.name)

            # Removed queryset limiting here. As per discussion re: #13023
            # on django-dev, max_num should not prevent existing
            # related objects/inlines from being displayed.
            self._queryset = qs
        return self._queryset

    def save_new(self, form, commit=True):
        """Saves and returns a new model instance for the given form."""
        return form.save(commit=commit)

    def save_existing(self, form, instance, commit=True):
        """Saves and returns an existing model instance for the given form."""
        return form.save(commit=commit)

    def save(self, commit=True):
        """Saves model instances for every form, adding and changing instances
        as necessary, and returns the list of instances.
        """
        if not commit:
            self.saved_forms = []
            def save_m2m():
                for form in self.saved_forms:
                    form.save_m2m()
            self.save_m2m = save_m2m
        return self.save_existing_objects(commit) + self.save_new_objects(commit)

    def clean(self):
        pass

    def get_form_error(self):
        return ugettext("Please correct the duplicate values below.")

    def save_existing_objects(self, commit=True):
        self.changed_objects = []
        self.deleted_objects = []
        if not self.get_queryset():
            return []

        saved_instances = []
        for i, form in enumerate(self.initial_forms):
            obj = self._existing_object(i)
            if self.can_delete and self._should_delete_form(form):
                self.deleted_objects.append(obj)
                #obj.delete()
                continue
            if form.has_changed():
                self.changed_objects.append((obj, form.changed_data))
            saved_instances.append(self.save_existing(form, obj, commit=commit))
            if not commit:
                self.saved_forms.append(form)
        return saved_instances

    def save_new_objects(self, commit=True):
        self.new_objects = []
        for form in self.extra_forms:
            if not form.has_changed():
                continue
            # If someone has marked an add form for deletion, don't save the
            # object.
            if self.can_delete and self._should_delete_form(form):
                continue
            self.new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects

    def add_fields(self, form, index):
        #CONSIDER there is no parent object, more like a document/instance and a dotpath
        """Add a hidden field for the object's primary key."""
        #TODO
        super(BaseDocumentFormSet, self).add_fields(form, index)

def documentformset_factory(document, form=DocumentForm, formfield_callback=None,
                         formset=BaseDocumentFormSet,
                         dotpath=None, schema=None,
                         extra=1, can_delete=False, can_order=False,
                         max_num=None, fields=None, exclude=None):
    """
    Returns a FormSet class for the given Document class.
    """
    form = documentform_factory(document, form=form, fields=fields, exclude=exclude,
                             dotpath=dotpath, schema=schema,
                             formfield_callback=formfield_callback)
    FormSet = formset_factory(form, formset, extra=extra, max_num=max_num,
                              can_order=can_order, can_delete=can_delete)
    FormSet.document = document
    return FormSet


# InlineFormSets #############################################################

class BaseInlineFormSet(BaseDocumentFormSet): #simply merge as one?
    """A formset for child objects related to a parent."""
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, dotpath=None):
        self.instance = instance
        self.save_as_new = save_as_new
        self.dotpath = dotpath or self.form._meta.dotpath
        # is there a better way to get the object descriptor?
        qs = self.instance.dot_notation(self.base_dotpath) or []
        super(BaseInlineFormSet, self).__init__(data, files, prefix=prefix,
                                                queryset=qs)
    
    @property
    def base_dotpath(self):
        return self.dotpath.rsplit('.', 1)[0]
    
    def initial_form_count(self):
        if self.save_as_new:
            return 0
        return super(BaseInlineFormSet, self).initial_form_count()

    def _construct_form(self, i, **kwargs):
        kwargs['dotpath'] = '%s.%i' % (self.base_dotpath, i)
        kwargs['instance'] = self.instance
        form = super(BaseDocumentFormSet, self)._construct_form(i, **kwargs)
        if self.save_as_new:
            # Remove the primary key from the form's data, we are only
            # creating new instances
            #form.data[form.add_prefix(self._pk_field.name)] = None

            # Remove the foreign key from the form's data
            #form.data[form.add_prefix(self.fk.name)] = None
            pass

        # Set the fk value here so that the form can do it's validation.
        #?????
        #setattr(form.instance, self.fk.get_attname(), self.instance.pk)
        return form

    #def get_default_prefix(self):
    #    return self.dotpath.rsplit('.', 1)[-1]
    #get_default_prefix = classmethod(get_default_prefix)
    
    def save_new(self, form, commit=True):
        """Saves and returns a new model instance for the given form."""
        return form._inner_save()

    def save_existing(self, form, instance, commit=True):
        """Saves and returns an existing model instance for the given form."""
        return form._inner_save()
    
    def save(self, commit=True, instance=None):
        """Saves model instances for every form, adding and changing instances
        as necessary, and returns the list of instances.
        """
        if instance:
            self.instance = instance
        if not commit:
            self.saved_forms = []
            def save_m2m():
                for form in self.saved_forms:
                    form.save_m2m()
            self.save_m2m = save_m2m
        new_list = self.save_existing_objects(commit) + self.save_new_objects(commit)
        if commit:
            self.instance.dot_notation_set_value(self.base_dotpath, new_list)
        return new_list


def inlinedocumentformset_factory(document, dotpath, form=DocumentForm,
                          formset=BaseInlineFormSet,
                          fields=None, exclude=None, schema=None,
                          extra=3, can_order=False, can_delete=True, max_num=None,
                          formfield_callback=None):
    """
    Returns an ``InlineFormSet`` for the given kwargs.

    You must provide ``fk_name`` if ``model`` has more than one ``ForeignKey``
    to ``parent_model``.
    """
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': formset,
        'extra': extra,
        'can_delete': can_delete,
        'can_order': can_order,
        'fields': fields,
        'exclude': exclude,
        'max_num': max_num,
        'schema': schema,
        'dotpath': dotpath + '.*',
    }
    FormSet = documentformset_factory(document, **kwargs)
    #FormSet.fk = fk
    return FormSet

