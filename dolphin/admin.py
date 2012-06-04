from django.contrib import admin
from django.conf import settings
from django import forms
from ajax_select import make_ajax_form

from .models import FeatureFlag

def enable_selected(modeladmin, request, queryset):
    queryset.update(enabled=True)
enable_selected.short_description = "Enable selected flags"

def disable_selected(modeladmin, request, queryset):
    queryset.update(enabled=False)
disable_selected.short_description = "Disable selected flags"



class FeatureFlagAdmin(admin.ModelAdmin):
    form = make_ajax_form(FeatureFlag, {'users':'user'})
    list_display = ('name', 'enabled', 'registered_only', 'staff_only', 'limit_to_users', 'enable_geo', 'is_ab_test')
    actions = [enable_selected, disable_selected]
    fieldsets = (
        (None, {
            'fields': ('name', 'enabled')
        }),
        ('User flags', {
            'fields': ('registered_only', 'staff_only', 'limit_to_users', 'users')
        }),
        ('A/B Tests', {
            'fields': ('is_ab_test', 'random', 'maximum_b_tests', 'current_b_tests', 'b_test_start', 'b_test_end')
        }),
    )

if getattr(settings, "DOLPHIN_USE_GIS", True):
    FeatureFlagAdmin.fieldsets += (
        ('Geolocation', {
            'fields': ('center_lat', 'center_lon', 'radius')
        }),
    )


admin.site.register(FeatureFlag, FeatureFlagAdmin)
