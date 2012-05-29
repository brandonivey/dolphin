from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from dolphin import flipper


class TestIsActive(TestCase):
    fixtures = ['base_flags.json']

    def test_is_active(self):
        self.assertTrue(flipper.is_active("enabled"))
        self.assertFalse(flipper.is_active("disabled"))
        self.assertFalse(flipper.is_active("missing"))

class TestUserFlags(TestCase):
    fixtures = ['users.json', 'user_flags.json']

    def _fake_request(self):
        req = type("Request", (object,), {})()
        return req

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
