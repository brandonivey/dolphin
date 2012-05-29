from django.db import models
from django.contrib.auth.models import User

class FeatureFlag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(blank=True, default=False)

    #users
    registered_only = models.BooleanField(blank=True, default=False)
    staff_only = models.BooleanField(blank=True, default=False)
    limit_to_users = models.BooleanField(blank=True, default=False)
    users = models.ManyToManyField(User) #TODO - do we want this to be many to many? possibly comma delimited charfield or something
