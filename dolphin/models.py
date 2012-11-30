import copy

from django.db import models
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete

from dolphin import settings
from dolphin.backends.utils import cache_key, Schema
from geoposition.fields import GeopositionField

class FeatureFlag(models.Model):
    name = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.CharField(max_length=150, default='', blank=True,
                  help_text="Description of the feature that is being flagged")
    enabled = models.BooleanField(blank=True, default=False, help_text="Flag is in use, if unchecked will be disabled altogether", db_index=True)
    expires = models.DateTimeField(blank=True, null=True, help_text="Notify in the admin when this flag expires on change list pages by displaying this value in red.")

    #Additional Options
    #users
    registered_only = models.BooleanField(blank=True, default=False, help_text="Limit to registered users")
    staff_only = models.BooleanField(blank=True, default=False, help_text="Limit to staff users")
    limit_to_group = models.BooleanField(blank=True, default=False, help_text="Limit to a specific group")
    group = models.ForeignKey(Group, blank=True, null=True)

    #geolocation
    enable_geo = models.BooleanField(blank=True, default=False, help_text="Enable geolocation")
    center = GeopositionField(null=True)
    radius = models.FloatField(blank=True, null=True, help_text="Distance in miles") #TODO - allow km/meters/etc

    #sites
    enable_for_sites = models.BooleanField(blank=True, default=False, help_text="If you wish to enable this flag for certain sites, please check this box and select the sites below.")
    disable_for_sites = models.BooleanField(blank=True, default=False, help_text="If you wish to disable this flag for certain sites, please check this box and select the sites below.")
    sites = models.ManyToManyField(Site, blank=True, null=True, help_text="Limit flag to these sites")

    #percent
    percent = models.IntegerField(blank=True, default=100,
                                  help_text=("Enable this feature to users based on a percentage"))
    cookie_max_age = models.IntegerField(blank=True, null=True, help_text="If this field is set, store the result of this flag in a browser's cookie until cookie_max_age(seconds), i.e., setting cookie_max_age=10 stores a cookie for this flag for 10 seconds.")

    #A/B testing stuff
    random = models.BooleanField(blank=True, default=False, help_text="Randomized A/B testing")
    maximum_b_tests = models.IntegerField(blank=True, null=True, help_text="Maximum number of B tests, use 0 for infinite")
    current_b_tests = models.IntegerField(blank=True, null=True, editable=True, help_text="Only updated if maximum_b_tests is set, updated once per view")
    b_test_start = models.DateTimeField(blank=True, null=True, db_index=True, help_text="Optional start date/time of B tests")
    b_test_end = models.DateTimeField(blank=True, null=True, db_index=True, help_text="Option end date/time of B tests")

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
