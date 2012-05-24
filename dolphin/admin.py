from django.contrib import admin

from .models import FeatureFlag


class FeatureFlagAdmin(admin.ModelAdmin):
    pass


admin.site.register(FeatureFlag, FeatureFlagAdmin)
