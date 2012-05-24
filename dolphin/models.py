from django.db import models

class FeatureFlag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(blank=True, default=False)
