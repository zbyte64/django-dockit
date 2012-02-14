from django.db import models

import dockit

class DocumentManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(DocumentManager, self).__init__(*args, **kwargs)
        self.index_models = dict()
    
    def register_index_model(self, key, model, instance_types):
        self.index_models[key] = {'model':model,
                                  'instance_types':instance_types}
    
    def get_index(self, key):
        return self.index_models[key]
    
    def filter_by_indexes(self, mapping, **filters):
        """
        mapping is a dictionary of the index as keys, and the datatype as the value
        """
        qs = self.all()
        for param, value in filters.iteritems():
            index = param.split('__', 1)[0]
            if index in mapping:
                key = mapping[index]
                qs &= self.filter_by_indexed_value(key, param, value)
            else:
                raise KeyError, "Unrecognized filter: %s" % index
        return qs
    
    def filter_by_indexed_value(self, key, index, value):
        model = self.get_index(key)['model']
        return self.filter(**model.objects.filter_kwargs_for_value(index, value))

class BaseIndexManager(models.Manager):
    def filter_kwargs_for_operation(self, operation):
        if operation.key in ('pk', '_pk'):
            return {'pk__%s' % operation.operation: operation.value}
        prefix = self.model._meta.get_field('document').related.var_name
        filter_kwargs = dict()
        filter_kwargs['%s__index' % prefix] = operation.key
        filter_kwargs['%s__value__%s' % (prefix, operation.operation)] = operation.value
        return filter_kwargs
    
    def unique_values(self, index):
        return self.filter(index=index).values_list('value', flat=True).distinct()
    
    def clear_db_index(self, instance_id, name=None):
        if name is None:
            return self.filter(document=instance_id).delete()
        return self.filter(document=instance_id, index=name).delete()
    
    def db_index(self, instance_id, name, value):
        if isinstance(value, models.Model):
            value = value.pk
        if isinstance(value, dockit.Document):
            value = value.pk
        self.filter(document=instance_id, index=name).delete()
        obj = self.create(document_id=instance_id, index=name, value=value)

