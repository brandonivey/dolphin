from django.utils.unittest import TestCase

from dolphin.models import FeatureFlag


class TestIsActive(TestCase):
    def test_is_active(self):

