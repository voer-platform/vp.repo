# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'APIToken.since'
        db.delete_column('vpc_api_apitoken', 'since')


    def backwards(self, orm):
        # Adding field 'APIToken.since'
        db.add_column('vpc_api_apitoken', 'since',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


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
            'token': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['vpc_api']