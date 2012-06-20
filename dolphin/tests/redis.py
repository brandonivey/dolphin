import datetime
import mock

from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404, HttpResponseRedirect
from django.test import TestCase

from dolphin import flipper
from dolphin.backends import RedisBackend
from dolphin.testutils import load_redis_fixtures
from dolphin.models import FeatureFlag
from dolphin.middleware import LocalStoreMiddleware
from dolphin import settings

from .flipper import (ActiveTest, UserFlagsTest, GeoIPTest,
    ABTest, CustomFlagTest, BaseTest)
from .templatetags import ActiveTagTest, FlagListTest


class BaseRedisTest(BaseTest):
    fixtures = ['base_flags.json']
    def __init__(self, *args, **kwargs):
        test_db = settings.DOLPHIN_REDIS_TEST_DB
        self.backend = RedisBackend(database=test_db)
        super(BaseRedisTest, self).__init__(*args, **kwargs)

    def setUp(self):
        LocalStoreMiddleware().clear()
        self.oldbackend = flipper.backend
        flipper.backend = self.backend
        super(BaseRedisTest, self).setUp()

    def tearDown(self):
        flipper.backend = self.oldbackend
        LocalStoreMiddleware().clear()
        super(BaseRedisTest, self).tearDown()

    def _get_redis(self):
        return self.backend._get_backend()

    def test_redis_is_active(self):
        r = self._get_redis()
        r.set('asdf', 'Test')
        self.assertEquals(r.get('asdf'), 'Test')


    def _fixture_setup(self):
        load_redis_fixtures(self.fixtures, self.backend)
        super(BaseRedisTest, self)._fixture_setup()

    def _fixture_teardown(self):
        self._get_redis().flushdb()
        super(BaseRedisTest, self)._fixture_teardown()

class RedisActiveTest(BaseRedisTest, ActiveTest):

    def test_create_missing(self):
        settings.DOLPHIN_AUTOCREATE_MISSING = True
        self.assertFalse(flipper.is_active('missing'))
        backend = flipper.backend._get_backend()
        val = backend.hgetall('missing')
        self.assertEquals(val['enabled'], 'False')
        self.assertEquals(val['name'], 'missing')
        settings.DOLPHIN_AUTOCREATE_MISSING = False

    def test_redis_fixture(self):
        self.assertTrue(flipper.is_active('enabled'))


class RedisUserFlagsTest(BaseRedisTest, UserFlagsTest):
    fixtures = ['users.json', 'user_flags.json']


class RedisGeoIPTest(BaseRedisTest, GeoIPTest):
    fixtures = ['regional_flags.json']


class RedisABTest(BaseRedisTest, ABTest):
    fixtures = ['ab_flags.json']

    def test_start(self):
        """Tests that the start datetime for A/B tests is working"""
        now = datetime.datetime.now()
        self.backend.update('start_passed', dict(name='start_passed', enabled=True, b_test_start=now-datetime.timedelta(days=1)))
        self.backend.update('start_tomorrow', dict(name='start_tomorrow', enabled=True, b_test_start=now+datetime.timedelta(days=1)))

        self.assertTrue(flipper.is_active('start_passed'))
        self.assertFalse(flipper.is_active('start_tomorrow'))

    def test_end(self):
        """Tests that the end datetime for A/B tests is working"""
        now = datetime.datetime.now()
        self.backend.update('end_passed', dict(name='end_passed', enabled=True, b_test_end=now-datetime.timedelta(days=1)))
        self.backend.update('end_tomorrow', dict(name='end_tomorrow', enabled=True, b_test_end=now+datetime.timedelta(days=1)))

        self.assertTrue(flipper.is_active('end_tomorrow'))
        self.assertFalse(flipper.is_active('end_passed'))

class RedisCustomFlagTest(BaseRedisTest, CustomFlagTest):
    pass

class RedisActiveTagTest(BaseRedisTest, ActiveTagTest):
    pass

class RedisFlagListTest(BaseRedisTest, FlagListTest):
    fixtures = ['users.json', 'user_flags.json', 'base_flags.json']

