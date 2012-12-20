# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'APIClient'
        db.create_table('vpc_api_apiclient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('organization', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('secret_key', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('vpc_api', ['APIClient'])

        # Adding model 'APIToken'
        db.create_table('vpc_api_apitoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpc_api.APIClient'])),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('client_ip', self.gf('django.db.models.fields.CharField')(max_length=48)),
            ('expire', self.gf('django.db.models.fields.DateTimeField')()),
            ('since', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('vpc_api', ['APIToken'])


    def backwards(self, orm):
        # Deleting model 'APIClient'
        db.delete_table('vpc_api_apiclient')

        # Deleting model 'APIToken'
        db.delete_table('vpc_api_apitoken')


    models = {
        'vpc_api.apiclient': {
            'Meta': {'object_name': 'APIClient'},
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'organization': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'vpc_api.apitoken': {
            'Meta': {'object_name': 'APIToken'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpc_api.APIClient']"}),
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'expire': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'since': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['vpc_api']