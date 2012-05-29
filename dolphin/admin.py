from django.contrib import admin

from .models import FeatureFlag


class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'registered_only', 'limit_to_users')


admin.site.register(FeatureFlag, FeatureFlagAdmin)
