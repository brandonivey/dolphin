from datetime import datetime

from django.contrib import admin
from dolphin import settings
from django import forms
from geoposition.fields import GeopositionField

from .models import FeatureFlag

def enable_selected(modeladmin, request, queryset):
    queryset.update(enabled=True)
enable_selected.short_description = "Enable selected flags"

def disable_selected(modeladmin, request, queryset):
    queryset.update(enabled=False)
disable_selected.short_description = "Disable selected flags"


class FeatureFlagForm(forms.ModelForm):
    center = GeopositionField()

    class Meta:
        model = FeatureFlag


class FeatureFlagAdmin(admin.ModelAdmin):
    form = FeatureFlagForm
    list_display = ('name', 'enabled', '_expires', 'registered_only', 'staff_only', 'limit_to_group', 'enable_geo')
    actions = [enable_selected, disable_selected]
    raw_id_fields = ('group',)
    fieldsets = (
        (None, {
            'fields': ('name', 'enabled', 'expires')
        }),
        ('User flags', {
            'fields': ('registered_only', 'staff_only', 'limit_to_group', 'group')
        }),
        ('A/B Tests', {
            'fields': ('random', 'maximum_b_tests', 'current_b_tests', 'b_test_start', 'b_test_end')
        }),
    )

    def _expires(self, obj):
        if obj.expires < datetime.now():
            return '<span style="color:red">%s</span>' % obj.expires
        return obj.expires
    _expires.allow_tags = True
    _expires.short_description = 'Expires'

if settings.DOLPHIN_USE_GIS:
    FeatureFlagAdmin.fieldsets += (
        ('Geolocation', {
            'fields': ('enable_geo', 'center', 'radius', )
        }),
    )


admin.site.register(FeatureFlag, FeatureFlagAdmin)
