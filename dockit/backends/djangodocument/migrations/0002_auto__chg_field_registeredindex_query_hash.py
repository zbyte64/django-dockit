# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'RegisteredIndex.query_hash'
        db.alter_column('djangodocument_registeredindex', 'query_hash', self.gf('django.db.models.fields.CharField')(max_length=128))

    def backwards(self, orm):

        # Changing field 'RegisteredIndex.query_hash'
        db.alter_column('djangodocument_registeredindex', 'query_hash', self.gf('django.db.models.fields.BigIntegerField')())

    models = {
        'djangodocument.booleanindex': {
            'Meta': {'object_name': 'BooleanIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'djangodocument.dateindex': {
            'Meta': {'object_name': 'DateIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.DateField', [], {'null': 'True'})
        },
        'djangodocument.datetimeindex': {
            'Meta': {'object_name': 'DateTimeIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'djangodocument.decimalindex': {
            'Meta': {'object_name': 'DecimalIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10'})
        },
        'djangodocument.documentstore': {
            'Meta': {'object_name': 'DocumentStore'},
            'collection': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'djangodocument.floatindex': {
            'Meta': {'object_name': 'FloatIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'djangodocument.integerindex': {
            'Meta': {'object_name': 'IntegerIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'djangodocument.longindex': {
            'Meta': {'object_name': 'LongIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
        },
        'djangodocument.registeredindex': {
            'Meta': {'unique_together': "[('name', 'collection')]", 'object_name': 'RegisteredIndex'},
            'collection': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'query_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djangodocument.registeredindexdocument': {
            'Meta': {'object_name': 'RegisteredIndexDocument'},
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'doc_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['djangodocument.RegisteredIndex']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'djangodocument.stringindex': {
            'Meta': {'object_name': 'StringIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'})
        },
        'djangodocument.textindex': {
            'Meta': {'object_name': 'TextIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'djangodocument.timeindex': {
            'Meta': {'object_name': 'TimeIndex'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangodocument.RegisteredIndexDocument']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TimeField', [], {'null': 'True'})
        }
    }

    complete_apps = ['djangodocument']