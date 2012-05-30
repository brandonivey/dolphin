from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from dolphin import flipper
from dolphin.models import FeatureFlag


class TestIsActive(TestCase):
    fixtures = ['base_flags.json']

    def test_is_active(self):
        self.assertTrue(flipper.is_active("enabled"))
        self.assertFalse(flipper.is_active("disabled"))
        self.assertFalse(flipper.is_active("missing"))

class BaseTest(TestCase):
    def _fake_request(self):
        req = type("Request", (object,), {})()
        return req

class TestUserFlags(BaseTest):
    fixtures = ['users.json', 'user_flags.json']


    def test_registered(self):
        req = self._fake_request()
        req.user = User.objects.get(username='registered')
        #registered user
        self.assertTrue(flipper.is_active("registered_only", request=req))
        #anonymous user
        req.user = AnonymousUser()
        self.assertFalse(flipper.is_active("registered_only", request=req))

    def test_staff(self):
        req = self._fake_request()
        req.user = User.objects.get(username='registered')
        #registered user
        self.assertFalse(flipper.is_active("staff_only", request=req))
        #anonymous user
        req.user = AnonymousUser()
        self.assertFalse(flipper.is_active("staff_only", request=req))
        #staff user
        req.user = User.objects.get(username="staff")
        self.assertTrue(flipper.is_active("staff_only", request=req))

    def test_users(self):
        req = self._fake_request()
        user = User.objects.get(username='registered')
        req.user = user
        self.assertTrue(flipper.is_active('selected_users', request=req))

        req.user = AnonymousUser()
        self.assertFalse(flipper.is_active('users', request=req))

        req.user = User.objects.get(username='staff')
        self.assertFalse(flipper.is_active('users', request=req))

class TestGeoIP(BaseTest):
    fixtures = ['regional_flags.json']

    def test_regional_flag(self):
        req = self._fake_request()
        req.META = {'REMOTE_ADDR':'4.2.2.2'}
        #within 100 miles of coord (69 or so)
        self.assertTrue(flipper.is_active('regional', request=req))

        req.META = {'REMOTE_ADDR':'0.0.0.0'}
        self.assertFalse(flipper.is_active('regional', request=req))

        req.META = {'REMOTE_ADDR':'74.125.227.39'}
        #not within 100 miles of coord
        self.assertFalse(flipper.is_active('regional', request=req))

        req.META = {'REMOTE_ADDR':'4.2.2.2'}
        #not within 5 miles of coord
        self.assertFalse(flipper.is_active('regional_5', request=req))
