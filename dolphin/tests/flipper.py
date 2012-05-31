import datetime
import mock

from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from dolphin import flipper
from dolphin.models import FeatureFlag


class IsActiveTest(TestCase):
    fixtures = ['base_flags.json']

    def test_is_active(self):
        self.assertTrue(flipper.is_active("enabled"))
        self.assertFalse(flipper.is_active("disabled"))
        self.assertFalse(flipper.is_active("missing"))

class BaseTest(TestCase):
    def _fake_request(self):
        req = type("Request", (object,), {})()
        return req

class UserFlagsTest(BaseTest):
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

class GeoIPTest(BaseTest):
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

class ABTest(BaseTest):
    fixtures = ['ab_flags.json']

    def test_start(self):
        """Tests that the start datetime for A/B tests is working"""
        now = datetime.datetime.now()
        FeatureFlag.objects.create(name='start_passed', enabled=True, is_ab_test=True, b_test_start=now-datetime.timedelta(days=1))
        FeatureFlag.objects.create(name='start_tomorrow', enabled=True, is_ab_test=True, b_test_start=now+datetime.timedelta(days=1))

        self.assertTrue(flipper.is_active('start_passed'))
        self.assertFalse(flipper.is_active('start_tomorrow'))

    def test_end(self):
        """Tests that the end datetime for A/B tests is working"""
        now = datetime.datetime.now()
        FeatureFlag.objects.create(name='end_passed', enabled=True, is_ab_test=True, b_test_end=now-datetime.timedelta(days=1))
        FeatureFlag.objects.create(name='end_tomorrow', enabled=True, is_ab_test=True, b_test_end=now+datetime.timedelta(days=1))

        self.assertTrue(flipper.is_active('end_tomorrow'))
        self.assertFalse(flipper.is_active('end_passed'))

    @mock.patch('random.random')
    def test_random(self, random):
        pass #TODO

    def test_max(self):
        """Tests that the max run for A/B tests is working"""
        for i in xrange(0, 5):
            self.assertTrue(flipper.is_active('max'))
        self.assertFalse(flipper.is_active('max'))
