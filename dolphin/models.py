from django.db import models
from django.contrib.auth.models import User

class FeatureFlag(models.Model):
    name = models.SlugField(max_length=255, unique=True)
    enabled = models.BooleanField(blank=True, default=False, help_text="Flag is in use, if unchecked will be disabled altogether")

    #users
    registered_only = models.BooleanField(blank=True, default=False, help_text="Limit to registered users")
    staff_only = models.BooleanField(blank=True, default=False, help_text="Limit to staff users")
    limit_to_users = models.BooleanField(blank=True, default=False, help_text="Limit to specific users")
    users = models.ManyToManyField(User, blank=True) #TODO - do we want this to be many to many? possibly comma delimited charfield or something

    def __unicode__(self):
        return self.name
