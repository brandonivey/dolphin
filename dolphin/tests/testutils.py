try:
    from django.test import TestCase
except ImportError:
    from django.utils.unittest import TestCase

from dolphin.testutils import set_active
from dolphin import flipper

class SetActiveTest(TestCase):
    def test_set_active(self):
        with set_active("test_flag", True):
            self.assertTrue(flipper.is_active('test_flag'))
        self.assertFalse(flipper.is_active('test_flag'))
