# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'APIClient'
        db.create_table('vpr_api_apiclient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('organization', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('secret_key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('join_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 14, 0, 0))),
        ))
        db.send_create_signal('vpr_api', ['APIClient'])

        # Adding model 'APIToken'
        db.create_table('vpr_api_apitoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_api.APIClient'])),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('client_ip', self.gf('django.db.models.fields.CharField')(max_length=48)),
            ('expire', self.gf('django.db.models.fields.DateTimeField')()),
            ('since', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('vpr_api', ['APIToken'])

        # Adding model 'APIRecord'
        db.create_table('vpr_api_apirecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('result', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('query', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('extra', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('vpr_api', ['APIRecord'])


    def backwards(self, orm):
        # Deleting model 'APIClient'
        db.delete_table('vpr_api_apiclient')

        # Deleting model 'APIToken'
        db.delete_table('vpr_api_apitoken')

        # Deleting model 'APIRecord'
        db.delete_table('vpr_api_apirecord')


    models = {
        'vpr_api.apiclient': {
            'Meta': {'object_name': 'APIClient'},
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'join_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 14, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'organization': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'vpr_api.apirecord': {
            'Meta': {'object_name': 'APIRecord'},
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'extra': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'vpr_api.apitoken': {
            'Meta': {'object_name': 'APIToken'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_api.APIClient']"}),
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'expire': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'since': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['vpr_api']