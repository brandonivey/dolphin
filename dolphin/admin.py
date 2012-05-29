from django.contrib import admin

from .models import FeatureFlag

def enable_selected(modeladmin, request, queryset):
    queryset.update(enabled=True)
enable_selected.short_description = "Enable selected flags"

def disable_selected(modeladmin, request, queryset):
    queryset.update(enabled=False)
disable_selected.short_description = "Disable selected flags"


class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'registered_only', 'staff_only', 'limit_to_users')
    actions = [enable_selected, disable_selected]
    fieldsets = (
        (None, {
            'fields': ('name', 'enabled')
        }),
        ('User flags', {
            'fields': ('registered_only', 'staff_only', 'limit_to_users', 'users')
        })
    )


    #TODO - add checking to make sure only one user checkbox is enabled

admin.site.register(FeatureFlag, FeatureFlagAdmin)
