from django.contrib import admin
from dolphin import settings
from django import forms
from geoposition.fields import GeopositionField
from ajax_select import make_ajax_field

from .models import FeatureFlag

def enable_selected(modeladmin, request, queryset):
    queryset.update(enabled=True)
enable_selected.short_description = "Enable selected flags"

def disable_selected(modeladmin, request, queryset):
    queryset.update(enabled=False)
disable_selected.short_description = "Disable selected flags"


class FeatureFlagForm(forms.ModelForm):
    center = GeopositionField()
    users = make_ajax_field(FeatureFlag, 'users', 'users', show_help_text = False, required=False)

    class Meta:
        model = FeatureFlag


class FeatureFlagAdmin(admin.ModelAdmin):
    #form = make_ajax_form(FeatureFlag, {'users':'user'})
    form = FeatureFlagForm
    list_display = ('name', 'enabled', 'registered_only', 'staff_only', 'limit_to_users', 'enable_geo')
    actions = [enable_selected, disable_selected]
    fieldsets = (
        (None, {
            'fields': ('name', 'enabled')
        }),
        ('User flags', {
            'fields': ('registered_only', 'staff_only', 'limit_to_users', 'users')
        }),
        ('A/B Tests', {
            'fields': ('random', 'maximum_b_tests', 'current_b_tests', 'b_test_start', 'b_test_end')
        }),
    )


if settings.DOLPHIN_USE_GIS:
    FeatureFlagAdmin.fieldsets += (
        ('Geolocation', {
            'fields': ('enable_geo', 'center', 'radius', )
        }),
    )


if not settings.DOLPHIN_USE_REDIS:
    admin.site.register(FeatureFlag, FeatureFlagAdmin)
