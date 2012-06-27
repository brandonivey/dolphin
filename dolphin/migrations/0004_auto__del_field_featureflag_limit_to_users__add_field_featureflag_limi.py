# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'FeatureFlag.limit_to_users'
        db.delete_column('dolphin_featureflag', 'limit_to_users')

        # Adding field 'FeatureFlag.limit_to_group'
        db.add_column('dolphin_featureflag', 'limit_to_group',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'FeatureFlag.group'
        db.add_column('dolphin_featureflag', 'group',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field users on 'FeatureFlag'
        db.delete_table('dolphin_featureflag_users')


    def backwards(self, orm):
        # Adding field 'FeatureFlag.limit_to_users'
        db.add_column('dolphin_featureflag', 'limit_to_users',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'FeatureFlag.limit_to_group'
        db.delete_column('dolphin_featureflag', 'limit_to_group')

        # Deleting field 'FeatureFlag.group'
        db.delete_column('dolphin_featureflag', 'group_id')

        # Adding M2M table for field users on 'FeatureFlag'
        db.create_table('dolphin_featureflag_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('featureflag', models.ForeignKey(orm['dolphin.featureflag'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('dolphin_featureflag_users', ['featureflag_id', 'user_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'enable_geo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_to_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maximum_b_tests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'random': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'registered_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['dolphin']