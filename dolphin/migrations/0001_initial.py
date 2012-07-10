# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'FeatureFlag'
        db.create_table('dolphin_featureflag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('registered_only', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('staff_only', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('limit_to_group', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True)),
            ('enable_geo', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('center', self.gf('geoposition.fields.GeopositionField')(max_length=42, null=True)),
            ('radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('random', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('maximum_b_tests', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('current_b_tests', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('b_test_start', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('b_test_end', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('dolphin', ['FeatureFlag'])


    def backwards(self, orm):

        # Deleting model 'FeatureFlag'
        db.delete_table('dolphin_featureflag')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dolphin.featureflag': {
            'Meta': {'object_name': 'FeatureFlag'},
            'b_test_end': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'b_test_start': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'center': ('geoposition.fields.GeopositionField', [], {'max_length': '42', 'null': 'True'}),
            'current_b_tests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'enable_geo': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_to_group': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'maximum_b_tests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'random': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'registered_only': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'staff_only': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['dolphin']
