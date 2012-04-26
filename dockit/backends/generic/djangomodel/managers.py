from django.db import models

import hashlib

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

class RegisteredIndexManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(RegisteredIndexManager, self).__init__(*args, **kwargs)
        self.index_models = dict()
    
    def register_index_model(self, key, model, instance_types):
        self.index_models[key] = {'model':model,
                                  'instance_types':instance_types}
    
    def get_index(self, key):
        return self.index_models[key]
    
    def serialize_query_index(self, query_index):
        pass
    
    def get_query_index_name(self, query_index):
        if query_index.name:
            return query_index.name
        data = self.serialize_query_index(query_index)
        #TODO check this code
        ahash = hashlib.md5(data)
        return ahash.hexdigest()
    
    def remove_index(self, query_index):
        name = self.get_query_index_name(query_index)
        collection = query_index.collection
        return self.filter(name=name, collection=collection).delete()
    
    def register_index(self, query_index):
        name = self.get_query_index_name(query_index)
        collection = query_index.collection
        serialized_query_index = self.serialize_query_index(query_index)
        #TODO the rest should be done in a task
        obj, created = self.get_or_create(name=name, collection=collection, defaults={'serialized_query_index':serialized_query_index})
        if not created:
            if obj.serialized_query_index == serialized_query_index:
                return
            obj.serialized_query_index = serialized_query_index
            for index in self.index_models.itervalues():
                index['model'].objects.filter(index=obj).delete()
            obj.save()
        
        #TODO do a reindex
        documents = list() #TODO
        for doc in documents:
            self.evaluate_query_index(obj, doc)
    
    def on_save(self, collection, doc_id, data, encoded_data):
        registered_queries = self.filter(collection=collection)
        for query in registered_queries:
            self.evaluate_query_index(query, data)
    
    def on_delete(self, collection, doc_id):
        registered_queries = self.filter(collection=collection)
        for index in self.index_models.itervalues():
            index['model'].objects.filter(index__in=registered_queries, doc_id=doc_id).delete()
    
    def evaluate_query_index(self, registered_query, data):
        pass
        #evaluate if document passes filters
        #index params

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
    
    def clear_db_index(self, name):
        return self.filter(index=name).delete()
    
    def clear_db_index_for_document(self, instance_id, name=None):
        if name is None:
            return self.filter(document=instance_id).delete()
        return self.filter(document=instance_id, index=name).delete()
    
    def db_index(self, instance_id, name, value):
        self.filter(document=instance_id, index=name).delete()
        from dockit.schema import Document
        if isinstance(value, models.Model):
            value = value.pk
        if isinstance(value, Document):
            value = value.pk
        obj = self.create(document_id=instance_id, index=name, value=value)

