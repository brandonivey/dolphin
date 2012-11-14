"""dolphin.tests.admin.py

Admin test class created for testing django-dolphin's admin functionality.

"""

from datetime import datetime, timedelta

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from dolphin.admin import FeatureFlagAdmin
from dolphin.models import FeatureFlag

class AdminTest(TestCase):
    fixtures = ['dolphin_base_flags.json']

    def setUp(self):
        now = datetime.now()
        self.ten_days_ago = now - timedelta(days=10)
        self.ten_days_later = now + timedelta(days=10)
        self.feature_flag = FeatureFlag.objects.all()[0]
        self.feature_flag_admin = FeatureFlagAdmin(FeatureFlag, AdminSite())

    def test_when_flag_expires(self):
        # when the feature flag expires, make sure that the admin reflects that.
        self.feature_flag.expires = self.ten_days_ago
        # the _expires function will return the object with red html mock up, so these values won't be equal.
        self.assertNotEqual(self.feature_flag_admin._expires(self.feature_flag), self.feature_flag)

    def test_when_flag_does_not_expires(self):
        # when the feature flag doesn't expire, make sure that the admin reflects that.
        self.feature_flag.expires = self.ten_days_later
        # the _expires function will just return the object.expires attr, so these values will be equal.
        self.assertNotEqual(self.feature_flag_admin._expires(self.feature_flag), self.feature_flag)
