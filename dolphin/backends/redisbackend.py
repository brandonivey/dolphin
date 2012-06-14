import redis
import random
import time
import datetime
import pytz
import re

from django.conf import settings as django_settings
from django.utils.datastructures import SortedDict
from geoposition import Geoposition

from .base import Backend
from dolphin import settings
from dolphin.utils import get_ip, get_geoip_coords, DefaultDict
from dolphin.middleware import LocalStoreMiddleware

def _initiate_redis(database=0):
    host = settings.DOLPHIN_REDIS_HOST
    port = settings.DOLPHIN_REDIS_PORT
    return redis.Redis(host=host, port=port, db=database)

class RedisSchema(object):

    @staticmethod
    def _bool(x):
        return True if x == 'True' else False

    bool_fields = set(('registered_only', 'enabled', 'staff_only', 'random',
                   'limit_to_users', 'enable_geo'))

    unicode_fields = set(('name',))
    datetime_fields = set(('b_test_start', 'b_test_end'))
    int_fields = set(('current_b_tests', 'maximum_b_tests'))
    float_fields = set(('radius',))
    none_fields = unicode_fields.union(datetime_fields).union(int_fields).union(float_fields)

    def parse(self, d):
        number_re = re.compile(r'(-?\d+(?:\.\d+)?)')
        for key in d.keys():
            if key in self.none_fields and d[key] == 'None':
                d[key] = None
                continue
            if key in self.bool_fields:
                d[key] = True if d[key] == 'True' else False
            elif key in self.unicode_fields:
                d[key] = unicode(d[key])
            elif key in self.datetime_fields:
                d[key] = datetime.datetime.fromtimestamp(float(d[key]))
            elif key in self.int_fields:
                d[key] = int(d[key])
            elif key in self.float_fields:
                d[key] = float(number_re.findall(d[key])[0])
            elif key == 'center':
                l = number_re.findall(d[key])
                #using a DefaultDict since the GeoPosition key is an object
                d[key] = Geoposition(float(l[0]), float(l[1]))
            elif key == 'users':
                d[key] = [int(i) for i in number_re.findall(d[key])]
        return d

    def serialize(self, d):
        for field in self.datetime_fields:
           if field in d and d[field] is not None:
               d[field] = d[field].strftime('%s')
        return d


class RedisBackend(Backend):
    def __init__(self, database=0):
        self.database = database

        self.initiator = getattr(django_settings, 'DOLPHIN_REDIS_CONNECT', _initiate_redis)
        self.store_flags = settings.DOLPHIN_STORE_FLAGS

        super(RedisBackend, self).__init__()

    def _get_backend(self):
        return self.initiator(database=self.database)

    def _get_redis_val(self, key):
        r = self._get_backend()
        val = r.hgetall(key)
        if val is None:
            return None

        return DefaultDict(RedisSchema().parse(val))

    def is_active(self, key, *args, **kwargs):
        #returns true if the key exists and is active, False otherwise
        val = self._get_redis_val(key)
        if val is None: return False

        request = self._get_request(**kwargs)
        return self._flag_is_active(val, request)

    def _flag_key(self, dd, request):
        """
        This creates a tuple key with various values to uniquely identify the request
        and flag
        """
        d = SortedDict()
        d['name'] = dd.name
        d['ip_address'] = get_ip(request)
        #avoid fake requests for tests
        if hasattr(request, 'user'):
            d['user_id'] = request.user.id
        else:
            d['user_id'] = None
        return tuple(d.values())

    def _flag_is_active(self, dd, request):
        """
        Checks the flag to see if it should be enabled or not.
        Encompases A/B tests, regional, and user based flags as well.
        Will only calculate random and max flags once per request.
        Will store flags for the request if DOLPHIN_STORE_FLAGS is True (default).
        """

        key = self._flag_key(dd, request)
        flags = LocalStoreMiddleware.local.setdefault('flags', {})

        if self.store_flags and key in flags:
            return flags[key]

        def store(val):
            """quick wrapper to store the flag results if it needs to"""
            if self.store_flags: flags[key] = val
            return val

        if not dd.enabled:
            return store(False)

        enabled = True
        if dd.registered_only or dd.limit_to_users or dd.staff_only:
            #user based flag
            if not request: enabled = False
            elif not request.user.is_authenticated():
                enabled = False
            else:
                if dd.limit_to_users and hasattr(dd.users, '__iter__'):
                    enabled = enabled and bool(request.user.id in dd.users)
                if dd.staff_only:
                    enabled = enabled and request.user.is_staff
                if dd.registered_only:
                    enabled = enabled and True

        if enabled == False: return store(enabled)

        if dd.enable_geo:
            #distance based
            x = get_geoip_coords(get_ip(request))
            if x is None or dd.center is None:
                enabled = False
            else:
                enabled = enabled and self._in_circle(dd, x[0], x[1])

        if enabled == False: return store(enabled)

        #A/B flags
        if dd.random:
            #doing this so that the random key is only calculated once per request
            def rand_bool():
                random.seed(time.time())
                return bool(random.randrange(0, 2))

            enabled = enabled and self._limit('random', dd.name, rand_bool, request)

        if dd.b_test_start:
            #start date
            if dd.b_test_start.tzinfo is not None:
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            else:
                now = datetime.datetime.now()
            enabled = enabled and now >= dd.b_test_start

        if dd.b_test_end:
            #end date
            if dd.b_test_end.tzinfo is not None:
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            else:
                now = datetime.datetime.now()
            enabled = enabled and now <= dd.b_test_end

        if dd.maximum_b_tests:
            #max B tests

            def maxb():
                r = self._get_backend()
                maxt = int(dd.maximum_b_tests)
                current_b_tests = int(dd.current_b_tests) if dd.current_b_tests is not None else 0
                if current_b_tests >= maxt:
                    return False

                if enabled:
                    return r.hincrby(dd.name, 'current_b_tests', 1) <=  maxt
                return True
            enabled = enabled and self._limit('maxb', dd.name, maxb, request)
        return store(enabled)

    def active_flags(self, *args, **kwargs):
        r = self._get_backend()
        setname = settings.DOLPHIN_SET_NAME
        flags = r.smembers(setname)
        req = self._get_request(**kwargs)
        red_vals = [self._get_redis_val(key) for key in flags]
        request = self._get_request(**kwargs)
        return [flag for flag in red_vals if self._flag_is_active(flag, request)]

    def update(self, key, d):
        d = RedisSchema().serialize(d)
        r = self._get_backend()
        if 'name' not in d:
            d['name'] = key
        r.hmset(key, d)
        setname = settings.DOLPHIN_SET_NAME
        r.sadd(setname, key)
