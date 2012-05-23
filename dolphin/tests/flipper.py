from django.utils.unittest import TestCase

from dolphin.models import FeatureFlag
from dolphin import flipper


class TestIsActive(TestCase):
    def setUp(self):
        FeatureFlag.objects.create(name="testing_enabled", enabled=True)
        FeatureFlag.objects.create(name="testing_disabled", enabled=False)

    def test_is_active(self):
        self.assertTrue(flipper.is_active("testing_enabled"))
        self.assertFalse(flipper.is_active("testing_disabled"))
        self.assertFalse(flipper.is_active("testing_missing"))
