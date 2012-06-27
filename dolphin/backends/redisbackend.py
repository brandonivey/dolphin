import redis
import random
import time
import datetime
import pytz

from django.conf import settings as django_settings
from django.utils.datastructures import SortedDict
from geoposition import Geoposition

from .base import Backend
from .utils import Schema
from dolphin import settings
from dolphin.utils import get_ip, get_geoip_coords, DefaultDict
from dolphin.middleware import LocalStoreMiddleware

def _initiate_redis(database=0):
    host = settings.DOLPHIN_REDIS_HOST
    port = settings.DOLPHIN_REDIS_PORT
    return redis.Redis(host=host, port=port, db=database)



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
        if val is None or val == {}:
            return None

        return DefaultDict(Schema().parse(val))

    def is_active(self, key, *args, **kwargs):
        #returns true if the key exists and is active, False otherwise
        val = self._get_redis_val(key)
        if val is None:
            if settings.DOLPHIN_AUTOCREATE_MISSING:
                self.update(key, {'name':key, 'enabled':False})
            return False

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
        if dd.registered_only or dd.limit_to_group or dd.staff_only:
            #user based flag
            if not request: enabled = False
            elif not request.user.is_authenticated():
                enabled = False
            else:
                if dd.limit_to_group:
                    enabled = enabled and bool(request.user.groups.filter(id=dd.group).exists())
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

    def get_names(self):
        r = self._get_backend()
        setname = settings.DOLPHIN_SET_NAME
        flags = r.smembers(setname)
        return flags

    def all_flags(self, *args, **kwargs):
        flags = self.get_names()
        req = self._get_request(**kwargs)
        red_vals = [self._get_redis_val(key) for key in flags]
        return red_vals

    def active_flags(self, *args, **kwargs):
        red_vals = self.all_flags(*args, **kwargs)
        request = self._get_request(**kwargs)
        return [flag for flag in red_vals if self._flag_is_active(flag, request)]

    def update(self, key, d):
        d = Schema().serialize(d)
        r = self._get_backend()
        if 'name' not in d:
            d['name'] = key
        r.hmset(key, d)
        setname = settings.DOLPHIN_SET_NAME
        r.sadd(setname, key)
