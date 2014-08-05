# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ExportFormat'
        db.create_table('vpr_content_exportformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('base_path', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('vpr_content', ['ExportFormat'])

        # Adding field 'MaterialExport.export_format'
        db.add_column('vpr_content_materialexport', 'export_format',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.ExportFormat'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ExportFormat'
        db.delete_table('vpr_content_exportformat')

        # Deleting field 'MaterialExport.export_format'
        db.delete_column('vpr_content_materialexport', 'export_format_id')


    models = {
        'vpr_content.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'vpr_content.exportformat': {
            'Meta': {'object_name': 'ExportFormat'},
            'base_path': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'vpr_content.material': {
            'Meta': {'object_name': 'Material'},
            'categories': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'derived_from': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'license_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'material_id': ('django.db.models.fields.CharField', [], {'default': "'d31e98d8'", 'max_length': '64'}),
            'material_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'vpr_content.materialcomment': {
            'Meta': {'object_name': 'MaterialComment'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Material']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Person']"})
        },
        'vpr_content.materialexport': {
            'Meta': {'object_name': 'MaterialExport'},
            'export_format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.ExportFormat']", 'null': 'True', 'blank': 'True'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'vpr_content.materialfavorite': {
            'Meta': {'object_name': 'MaterialFavorite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Material']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Person']"})
        },
        'vpr_content.materialfile': {
            'Meta': {'object_name': 'MaterialFile'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'mfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'vpr_content.materialperson': {
            'Meta': {'object_name': 'MaterialPerson'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material_rid': ('django.db.models.fields.IntegerField', [], {}),
            'person_id': ('django.db.models.fields.IntegerField', [], {}),
            'role': ('django.db.models.fields.IntegerField', [], {})
        },
        'vpr_content.materialrating': {
            'Meta': {'object_name': 'MaterialRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Material']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Person']"}),
            'rate': ('django.db.models.fields.IntegerField', [], {})
        },
        'vpr_content.materialviewcount': {
            'Meta': {'object_name': 'MaterialViewCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'last_visit': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'material': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vpr_content.Material']", 'primary_key': 'True'})
        },
        'vpr_content.originalid': {
            'Meta': {'object_name': 'OriginalID'},
            'material_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'original_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'vpr_content.person': {
            'Meta': {'object_name': 'Person'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'affiliation_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'biography': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'client_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'homepage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'national': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['vpr_content']