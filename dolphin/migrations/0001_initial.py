# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeatureFlag'
        db.create_table('dolphin_featureflag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('registered_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('staff_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('limit_to_users', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_geo', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('center_lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('center_lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('is_ab_test', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('random', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('maximum_b_tests', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('current_b_tests', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('b_test_start', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('b_test_end', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('dolphin', ['FeatureFlag'])

        # Adding M2M table for field users on 'FeatureFlag'
        db.create_table('dolphin_featureflag_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('featureflag', models.ForeignKey(orm['dolphin.featureflag'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('dolphin_featureflag_users', ['featureflag_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'FeatureFlag'
        db.delete_table('dolphin_featureflag')

        # Removing M2M table for field users on 'FeatureFlag'
        db.delete_table('dolphin_featureflag_users')


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
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'center_lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'center_lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'current_b_tests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'enable_geo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ab_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'limit_to_users': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maximum_b_tests': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'random': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'registered_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['dolphin']