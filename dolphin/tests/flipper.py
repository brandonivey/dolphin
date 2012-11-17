import datetime
import mock

from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404, HttpResponseRedirect, HttpResponse, SimpleCookie
from django.test import TestCase

from dolphin import flipper
from dolphin import settings
from dolphin.models import FeatureFlag
from dolphin.middleware import LocalStoreMiddleware



class BaseTest(TestCase):
    def _fake_request(self):
        req = type("Request", (object,), {})()
        return req

    def setUp(self):
        flipper.registered_checks = {}
        LocalStoreMiddleware.local.clear()

    def tearDown(self):
        flipper.registered_checks = {}
        LocalStoreMiddleware.local.clear()


class ActiveTest(BaseTest):
    fixtures = ['dolphin_base_flags.json']

    def test_create_missing(self):
        settings.DOLPHIN_AUTOCREATE_MISSING = True
        self.assertFalse(flipper.is_active('missing'))
        self.assertTrue(FeatureFlag.objects.filter(name='missing').exists())
        settings.DOLPHIN_AUTOCREATE_MISSING = False

    def test_is_active(self):
        self.assertTrue(flipper.is_active("enabled"))
        self.assertFalse(flipper.is_active("disabled"))
        self.assertFalse(flipper.is_active("missing"))

    def test_switch_is_active(self):
        outer = "Outer"
        f1 = lambda: "f1"
        f2 = lambda: "f2"

        wrapped_f1 = flipper.switch_is_active('disabled')(f1)
        self.assertRaises(Http404, wrapped_f1)

        wrapped_f1 = flipper.switch_is_active('disabled', alt=f2)(f1)
        self.assertEquals(wrapped_f1(), "f2")

        wrapped_f1 = flipper.switch_is_active('disabled', redirect='/')(f1)
        self.assertTrue(isinstance(wrapped_f1(), HttpResponseRedirect))

        wrapped_f1 = flipper.switch_is_active('enabled', redirect='/')(f1)
        self.assertEquals(wrapped_f1(), "f1")

    def test_ifactive(self):
        self.assertEquals(flipper.ifactive('enabled', 'Active', 'Disabled'), 'Active')
        self.assertEquals(flipper.ifactive('disabled', 'Active', 'Disabled'), 'Disabled')
        self.assertEquals(flipper.ifactive('missing', 'Active', 'Disabled'), 'Disabled')


class UserFlagsTest(BaseTest):
    fixtures = ['dolphin_users.json', 'dolphin_user_flags.json']

    def test_registered(self):
        #Tests the registered user only flags
        req = self._fake_request()
        req.user = User.objects.get(username='registered')
        #registered user
        self.assertTrue(flipper.is_active("registered_only", request=req))
        #anonymous user
        req.user = AnonymousUser()
        self.assertFalse(flipper.is_active("registered_only", request=req))

    def test_staff(self):
        #Tests the staff only flags
        settings.DOLPHIN_STORE_FLAGS=False
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
        #Tests the user specific flags
        req = self._fake_request()
        user = User.objects.get(username='registered')
        req.user = user
        self.assertTrue(flipper.is_active('selected_group', request=req))

        req.user = AnonymousUser()
        self.assertFalse(flipper.is_active('users', request=req))

        req.user = User.objects.get(username='staff')
        self.assertFalse(flipper.is_active('users', request=req))


class GeoIPTest(BaseTest):
    fixtures = ['dolphin_regional_flags.json']

    def test_regional_flag(self):
        try:
            from django.contrib.gis.utils import geoip
            if hasattr(geoip,'HAS_GEOIP') and not geoip.HAS_GEOIP:
                return self.skipTest('GIS not installed. Skipping GeoIPTest')
        except Exception:
            return self.skipTest('GIS not installed. Skipping GeoIPTest')

        #Tests that the regional flag works properly for IP address detection and distance
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
    fixtures = ['dolphin_ab_flags.json']

    def test_start(self):
        #Tests that the start datetime for A/B tests is working
        now = datetime.datetime.now()
        FeatureFlag.objects.create(name='start_passed', enabled=True, b_test_start=now-datetime.timedelta(days=1))
        FeatureFlag.objects.create(name='start_tomorrow', enabled=True, b_test_start=now+datetime.timedelta(days=1))

        self.assertTrue(flipper.is_active('start_passed'))
        self.assertFalse(flipper.is_active('start_tomorrow'))

    def test_end(self):
        #Tests that the end datetime for A/B tests is working
        now = datetime.datetime.now()
        FeatureFlag.objects.create(name='end_passed', enabled=True, b_test_end=now-datetime.timedelta(days=1))
        FeatureFlag.objects.create(name='end_tomorrow', enabled=True, b_test_end=now+datetime.timedelta(days=1))

        self.assertTrue(flipper.is_active('end_tomorrow'))
        self.assertFalse(flipper.is_active('end_passed'))

    @mock.patch('random.randrange')
    def test_random(self, randrange):
        #Tests that the random flag is working correctly
        randrange.return_value = 1
        self.assertTrue(flipper.is_active('ab_random'))

        LocalStoreMiddleware.local.clear()
        randrange.return_value = 0
        self.assertFalse(flipper.is_active('ab_random'))

    def test_max(self):
        #Tests that the max run for A/B tests is working
        for i in xrange(0, 5):
            self.assertTrue(flipper.is_active('max'))
            LocalStoreMiddleware.local.clear()

        self.assertFalse(flipper.is_active('max'))

class CookiesTest(BaseTest):
    """Make sure dolphin knows what to do with cookies"""

    @mock.patch('random.uniform')
    def test_cookies_in_local_store(self, uniform):
        #Verify that cookies are being stored in dolphin's local store correctly
        FeatureFlag.objects.create(name='cookie_flag', enabled=True, percent=50)
        uniform.return_value = 1
        cookie_prefix = getattr(settings, 'DOLPHIN_COOKIE', 'dolphin_%s')
        cookie = cookie_prefix % 'cookie_flag'
        is_active = flipper.is_active('cookie_flag')
        self.assertEqual(LocalStoreMiddleware.local.get('dolphin_cookies')[cookie][0], is_active)

    def test_cookies_in_middleware(self):
        #Verify that cookies are being stored via dolphin's middleware response process
        middleware = LocalStoreMiddleware()
        req = self._fake_request()
        resp = HttpResponse()
        now = datetime.datetime.now()
        ten_days_later = now+datetime.timedelta(days=10)
        cookies = {'dolphin_test_cookie1':(True,ten_days_later), 'dolphin_test_cookie2':(False,ten_days_later)}
        LocalStoreMiddleware.local.setdefault('dolphin_cookies', cookies)
        response = middleware.process_response(req, resp)
        self.assertEqual(response.cookies.keys(), SimpleCookie(cookies).keys())
        #Clear cookies
        response.cookies = {}
        #Verify that we've cleaned up the cookies
        self.assertNotEqual(response.cookies.keys(), SimpleCookie(cookies).keys())

    def test_cookies_being_retrieved_properly(self):
        #Verify that cookies are being retrieved properly
        cookie_prefix = getattr(settings, 'DOLPHIN_COOKIE', 'dolphin_%s')
        cookie = cookie_prefix % 'cookie_flag'
        FeatureFlag.objects.create(name='cookie_flag', enabled=True, percent=100)
        req = self._fake_request()
        #Cookie values take precedent over the is_active logic with a simple short circuit
        req.COOKIES = {cookie: False}
        self.assertFalse(flipper.is_active('cookie_flag', request=req))
        req.COOKIES = {cookie: True}
        self.assertTrue(flipper.is_active('cookie_flag', request=req))

class RollOutTest(BaseTest):
    """Test the roll out feature"""

    @mock.patch('random.uniform')
    def test_random_percent(self, uniform):
        #Tests that the feature is active for random percentages
        req = self._fake_request()
        FeatureFlag.objects.create(name='ab_percent', enabled=True, percent=50)
        uniform.return_value = 1
        #Need a request object to store the flag cookie
        self.assertTrue(flipper.is_active('ab_percent'))

        LocalStoreMiddleware.local.clear()

        uniform.return_value = 51
        #Need a request object to store the cookie
        self.assertFalse(flipper.is_active('ab_percent'))

    def test_100_percent(self):
        #Tests that the feature is active when the percent is set to 100
        FeatureFlag.objects.create(name='ab_percent', enabled=True, percent=100)
        self.assertTrue(flipper.is_active('ab_percent'))

    def test_0_percent(self):
        #Tests that the feature is not active for when the percent value is set to 0
        FeatureFlag.objects.create(name='ab_percent', enabled=True, percent=0)
        self.assertFalse(flipper.is_active('ab_percent'))

class CustomFlagTest(BaseTest):
    fixtures = ['dolphin_base_flags.json']

    def test_enabled_custom_flag(self):
        #base test
        self.assertTrue(flipper.is_active("enabled"))
        flipper.register_check('enabled', lambda x, **kwargs: True)
        flipper.register_check('disabled', lambda x, **kwargs: True)
        self.assertTrue(flipper.is_active('enabled'))
        self.assertFalse(flipper.is_active('disabled'))


        flipper.register_check('enabled', lambda x, **kwargs: False)
        self.assertFalse(flipper.is_active('enabled'))

