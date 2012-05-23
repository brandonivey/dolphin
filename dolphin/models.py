from django.db import models

class FeatureFlag(models.Model):
    name = models.CharField(max_length=255)
    enabled = models.BooleanField(blank=True, default=False)
