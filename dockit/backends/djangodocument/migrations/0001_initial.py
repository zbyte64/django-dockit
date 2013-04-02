# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocumentStore'
        db.create_table('djangodocument_documentstore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangodocument', ['DocumentStore'])

        # Adding model 'RegisteredIndex'
        db.create_table('djangodocument_registeredindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('collection', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('query_hash', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('djangodocument', ['RegisteredIndex'])

        # Adding unique constraint on 'RegisteredIndex', fields ['name', 'collection']
        db.create_unique('djangodocument_registeredindex', ['name', 'collection'])

        # Adding model 'RegisteredIndexDocument'
        db.create_table('djangodocument_registeredindexdocument', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('index', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['djangodocument.RegisteredIndex'])),
            ('doc_id', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('djangodocument', ['RegisteredIndexDocument'])

        # Adding model 'IntegerIndex'
        db.create_table('djangodocument_integerindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['IntegerIndex'])

        # Adding model 'LongIndex'
        db.create_table('djangodocument_longindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['LongIndex'])

        # Adding model 'BooleanIndex'
        db.create_table('djangodocument_booleanindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('djangodocument', ['BooleanIndex'])

        # Adding model 'StringIndex'
        db.create_table('djangodocument_stringindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=512, null=True)),
        ))
        db.send_create_signal('djangodocument', ['StringIndex'])

        # Adding model 'TextIndex'
        db.create_table('djangodocument_textindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['TextIndex'])

        # Adding model 'DateTimeIndex'
        db.create_table('djangodocument_datetimeindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['DateTimeIndex'])

        # Adding model 'DateIndex'
        db.create_table('djangodocument_dateindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['DateIndex'])

        # Adding model 'FloatIndex'
        db.create_table('djangodocument_floatindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['FloatIndex'])

        # Adding model 'TimeIndex'
        db.create_table('djangodocument_timeindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.TimeField')(null=True)),
        ))
        db.send_create_signal('djangodocument', ['TimeIndex'])

        # Adding model 'DecimalIndex'
        db.create_table('djangodocument_decimalindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangodocument.RegisteredIndexDocument'])),
            ('param_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=10)),
        ))
        db.send_create_signal('djangodocument', ['DecimalIndex'])


    def backwards(self, orm):
        # Removing unique constraint on 'RegisteredIndex', fields ['name', 'collection']
        db.delete_unique('djangodocument_registeredindex', ['name', 'collection'])

        # Deleting model 'DocumentStore'
        db.delete_table('djangodocument_documentstore')

        # Deleting model 'RegisteredIndex'
        db.delete_table('djangodocument_registeredindex')

        # Deleting model 'RegisteredIndexDocument'
        db.delete_table('djangodocument_registeredindexdocument')

        # Deleting model 'IntegerIndex'
        db.delete_table('djangodocument_integerindex')

        # Deleting model 'LongIndex'
        db.delete_table('djangodocument_longindex')

        # Deleting model 'BooleanIndex'
        db.delete_table('djangodocument_booleanindex')

        # Deleting model 'StringIndex'
        db.delete_table('djangodocument_stringindex')

        # Deleting model 'TextIndex'
        db.delete_table('djangodocument_textindex')

        # Deleting model 'DateTimeIndex'
        db.delete_table('djangodocument_datetimeindex')

        # Deleting model 'DateIndex'
        db.delete_table('djangodocument_dateindex')

        # Deleting model 'FloatIndex'
        db.delete_table('djangodocument_floatindex')

        # Deleting model 'TimeIndex'
        db.delete_table('djangodocument_timeindex')

        # Deleting model 'DecimalIndex'
        db.delete_table('djangodocument_decimalindex')


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
            'query_hash': ('django.db.models.fields.BigIntegerField', [], {})
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