# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('vpr_content_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('vpr_content', ['Category'])

        # Adding model 'Person'
        db.create_table('vpr_content_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('homepage', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('affiliation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('affiliation_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('national', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('biography', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('client_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('vpr_content', ['Person'])

        # Adding model 'Material'
        db.create_table('vpr_content_material', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material_id', self.gf('django.db.models.fields.CharField')(default='2109611c', max_length=64)),
            ('material_type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('categories', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('license_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('derived_from', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('vpr_content', ['Material'])

        # Adding model 'OriginalID'
        db.create_table('vpr_content_originalid', (
            ('material_id', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
            ('original_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('vpr_content', ['OriginalID'])

        # Adding model 'MaterialFile'
        db.create_table('vpr_content_materialfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mfile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('vpr_content', ['MaterialFile'])

        # Adding model 'MaterialExport'
        db.create_table('vpr_content_materialexport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file_type', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('vpr_content', ['MaterialExport'])

        # Adding model 'MaterialPerson'
        db.create_table('vpr_content_materialperson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material_rid', self.gf('django.db.models.fields.IntegerField')()),
            ('person_id', self.gf('django.db.models.fields.IntegerField')()),
            ('role', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('vpr_content', ['MaterialPerson'])

        # Adding model 'MaterialComment'
        db.create_table('vpr_content_materialcomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Material'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Person'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
        ))
        db.send_create_signal('vpr_content', ['MaterialComment'])

        # Adding model 'MaterialRating'
        db.create_table('vpr_content_materialrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Material'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Person'])),
            ('rate', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('vpr_content', ['MaterialRating'])

        # Adding model 'MaterialFavorite'
        db.create_table('vpr_content_materialfavorite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('material', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Material'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Person'])),
        ))
        db.send_create_signal('vpr_content', ['MaterialFavorite'])

        # Adding model 'MaterialViewCount'
        db.create_table('vpr_content_materialviewcount', (
            ('material', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['vpr_content.Material'], primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('last_visit', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
        ))
        db.send_create_signal('vpr_content', ['MaterialViewCount'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('vpr_content_category')

        # Deleting model 'Person'
        db.delete_table('vpr_content_person')

        # Deleting model 'Material'
        db.delete_table('vpr_content_material')

        # Deleting model 'OriginalID'
        db.delete_table('vpr_content_originalid')

        # Deleting model 'MaterialFile'
        db.delete_table('vpr_content_materialfile')

        # Deleting model 'MaterialExport'
        db.delete_table('vpr_content_materialexport')

        # Deleting model 'MaterialPerson'
        db.delete_table('vpr_content_materialperson')

        # Deleting model 'MaterialComment'
        db.delete_table('vpr_content_materialcomment')

        # Deleting model 'MaterialRating'
        db.delete_table('vpr_content_materialrating')

        # Deleting model 'MaterialFavorite'
        db.delete_table('vpr_content_materialfavorite')

        # Deleting model 'MaterialViewCount'
        db.delete_table('vpr_content_materialviewcount')


    models = {
        'vpr_content.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'material_id': ('django.db.models.fields.CharField', [], {'default': "'081590c5'", 'max_length': '64'}),
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