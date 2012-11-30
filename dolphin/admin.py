from datetime import datetime

from django.contrib import admin
from django.conf import settings as django_settings
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
    class Media:
        #TODO: change django_settings.ADMIN_TOOLS_MEDIA_URL to a more standard setting like STATIC_URL
        #settings.ADMIN_TOOLS_MEDIA_URL is medley specific.
        js = (
            '%sdolphin/js/geoposition.js' % django_settings.ADMIN_TOOLS_MEDIA_URL,
            '%sdolphin/js/dolphin.admin.js' % django_settings.ADMIN_TOOLS_MEDIA_URL,
            '%sjavascript/jquery/ui/jquery-ui-1.8.4.custom.js' % django_settings.ADMIN_TOOLS_MEDIA_URL
            )

        css = {
            "all": ('%sdolphin/css/geoposition.css' % django_settings.ADMIN_TOOLS_MEDIA_URL,
                    '%scss/jquery-ui-1.8.4.custom.css ' % django_settings.ADMIN_TOOLS_MEDIA_URL)
            }

    form = FeatureFlagForm
    list_display = ('name', 'description', 'enabled', '_expires', 'registered_only', 'staff_only', 'limit_to_group', 'enable_geo')
    filter_horizontal = ('sites',)
    actions = [enable_selected, disable_selected]
    raw_id_fields = ('group',)
    fieldsets = (
        ('Metadata', {
            'fields': ('name', 'description', 'enabled', 'expires')
        }),
        ('Options', {
            'classes': ('collapse',),
            'fields': ('registered_only', 'staff_only', 'limit_to_group', 'group', 'percent', 'enable_for_sites', 'disable_for_sites', 'sites', 'cookie_max_age')
        }),
        ('A/B Tests', {
            'classes': ('collapse',),
            'fields': ('random', 'maximum_b_tests', 'current_b_tests', 'b_test_start', 'b_test_end')
        }),
    )

    def _sites_display(self, obj):
        return ", ".join([sites.domain for sites in sites.all()])
    _sites_display.short_description = 'Sites'

    def _expires(self, obj):
        if obj.expires and obj.expires < datetime.now():
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
