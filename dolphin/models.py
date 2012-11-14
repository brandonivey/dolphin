import copy

from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import Group
from geoposition.fields import GeopositionField
from django.db.models.signals import post_save, post_delete

from dolphin import settings
from dolphin.backends.utils import cache_key, Schema


class FeatureFlag(models.Model):
    name = models.SlugField(max_length=255, unique=True, db_index=True)
    enabled = models.BooleanField(blank=True, default=False, help_text="Flag is in use, if unchecked will be disabled altogether", db_index=True)
    expires = models.DateTimeField(blank=True, null=True, db_index=True, help_text = "Displays a warning when this feature expires")

    #users
    registered_only = models.BooleanField(blank=True, default=False, help_text="Limit to registered users")
    staff_only = models.BooleanField(blank=True, default=False, help_text="Limit to staff users")
    limit_to_group = models.BooleanField(blank=True, default=False, help_text="Limit to a specific group")
    group = models.ForeignKey(Group, blank=True, null=True)

    #geolocation
    enable_geo = models.BooleanField(blank=True, default=False, help_text="Enable geolocation")
    center = GeopositionField(null=True)
    radius = models.FloatField(blank=True, null=True, help_text="Distance in miles") #TODO - allow km/meters/etc

    #A/B testing stuff
    random = models.BooleanField(blank=True, default=False, help_text="Randomized A/B testing")
    percent = models.IntegerField(blank=True, default=100,
                                  help_text=('A number between 0 and 100 to indicate a percentage of users for whom this flag will be active.  Default is set to 100 to enable this feature for everyone.'))
    maximum_b_tests = models.IntegerField(blank=True, null=True, help_text="Maximum number of B tests, use 0 for infinite")
    current_b_tests = models.IntegerField(blank=True, null=True, editable=True, help_text="Only updated if maximum_b_tests is set, updated once per view")
    b_test_start = models.DateTimeField(blank=True, null=True, db_index=True, help_text = "Optional start date/time of B tests")
    b_test_end = models.DateTimeField(blank=True, null=True, db_index=True, help_text = "Option end date/time of B tests")

    def __unicode__(self):
        return self.name


def delete_cache_receiver(sender, instance, **kwargs):
    if settings.DOLPHIN_CACHE:
        cache.delete(cache_key(instance.name))

def update_cache_receiver(sender, instance, **kwargs):
    if settings.DOLPHIN_CACHE and instance.id:
        cache.set(cache_key(instance.name), Schema().serialize(copy.copy(instance.__dict__)))

post_save.connect(update_cache_receiver, sender=FeatureFlag)
post_delete.connect(delete_cache_receiver, sender=FeatureFlag)
