from django.test import TestCase

from dolphin.models import FeatureFlag
from dolphin import flipper


class TestIsActive(TestCase):
    fixtures = ['flags.json']

    def test_is_active(self):
        self.assertTrue(flipper.is_active("testing_enabled"))
        self.assertFalse(flipper.is_active("testing_disabled"))
        self.assertFalse(flipper.is_active("testing_missing"))
