import datetime
import random
import time
import pytz
import copy

from django.utils.datastructures import SortedDict
from django.db.models import F
from django.core.cache import cache

from dolphin import settings
from dolphin.models import FeatureFlag
from dolphin.middleware import LocalStoreMiddleware
from dolphin.utils import get_ip, get_geoip_coords, DefaultDict
from .utils import Schema, cache_key
from .base import Backend


class DjangoBackend(Backend):
    """
    A basic django backend that tests if a flag is set
    The only caching done with this backend is a per-request
    cache for each flag if DOLPHIN_STORE_FLAGS is True.
    """

    def _flag_key(self, ff, request):
        """
        This creates a tuple key with various values to uniquely identify the request
        and flag
        """
        d = SortedDict()
        d['name'] = ff.name
        d['ip_address'] = get_ip(request)
        #avoid fake requests for tests
        if hasattr(request, 'user'):
            d['user_id'] = request.user.id
        else:
            d['user_id'] = None
        return tuple(d.values())

    def _flag_is_active(self, ff, request):
        """
        Checks the flag to see if it should be enabled or not.
        Encompases A/B tests, regional, and user based flags as well.
        Will only calculate random and max flags once per request.
        Will store flags for the request if DOLPHIN_STORE_FLAGS is True (default).
        """

        key = self._flag_key(ff, request)
        flags = LocalStoreMiddleware.local.setdefault('flags', {})
        store_flags = settings.DOLPHIN_STORE_FLAGS

        if store_flags and key in flags:
            return flags[key]

        def store(val):
            """quick wrapper to store the flag results if it needs to"""
            if store_flags: flags[key] = val
            return val

        if not ff.enabled:
            return store(False)

        enabled = True
        if ff.registered_only or ff.limit_to_users or ff.staff_only:
            #user based flag
            if not request: enabled = False
            elif not request.user.is_authenticated():
                enabled = False
            else:
                if ff.limit_to_users:
                    enabled = enabled and bool(ff.users.filter(id=request.user.id).exists())
                if ff.staff_only:
                    enabled = enabled and request.user.is_staff
                if ff.registered_only:
                    enabled = enabled and True

        if enabled == False: return store(enabled)

        if ff.enable_geo:
            #distance based
            x = get_geoip_coords(get_ip(request))
            if x is None:
                enabled = False
            else:
                enabled = enabled and self._in_circle(ff, x[0], x[1])

        if enabled == False: return store(enabled)

        #A/B flags
        if ff.random:
            #doing this so that the random key is only calculated once per request
            def rand_bool():
                random.seed(time.time())
                return bool(random.randrange(0, 2))

            enabled = enabled and self._limit('random', ff.name, rand_bool, request)

        if ff.b_test_start:
            #start date
            if ff.b_test_start.tzinfo is not None:
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            else:
                now = datetime.datetime.now()
            enabled = enabled and now >= ff.b_test_start

        if ff.b_test_end:
            #end date
            if ff.b_test_end.tzinfo is not None:
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            else:
                now = datetime.datetime.now()
            enabled = enabled and now <= ff.b_test_end

        if ff.maximum_b_tests:
            #max B tests
            #TODO - is this worth becoming atomic and locking?

            def maxb():
                maxt = ff.maximum_b_tests
                if ff.current_b_tests >= ff.maximum_b_tests:
                    return False

                if enabled:
                    FeatureFlag.objects.filter(id=ff.id).update(current_b_tests=F('current_b_tests')+1)
                    if settings.DOLPHIN_CACHE:
                        cache.delete(cache_key(ff.name))
                return True
            enabled = enabled and self._limit('maxb', ff.name, maxb, request)

        return store(enabled)

    def is_active(self, key, *args, **kwargs):
        """checks if a flag is active by the name of key"""
        #allows for the with() statement to override in tests
        overrides = LocalStoreMiddleware.local.setdefault('overrides', {})
        if key in overrides:
            return overrides[key]

        try:
            req = self._get_request(**kwargs)
            if settings.DOLPHIN_CACHE:
                ff = cache.get(cache_key(key))
                if ff is not None:
                    return self._flag_is_active(DefaultDict(Schema().parse(ff)), req)

            ff = FeatureFlag.objects.get(name=key)
            if settings.DOLPHIN_CACHE:
                cache.set(cache_key(key), Schema().serialize(copy.copy(ff.__dict__)))

            return self._flag_is_active(ff, req)

        except FeatureFlag.DoesNotExist:
            if settings.DOLPHIN_AUTOCREATE_MISSING:
                FeatureFlag.objects.create(name=key, enabled=False)
            return False

    def delete(self, key, *args, **kwargs):
        FeatureFlag.objects.filter(name=key).delete()
        #just delete the store and make them recalculate
        del LocalStoreMiddleware.local['flags']

    def active_flags(self, *args, **kwargs):
        flags = FeatureFlag.objects.filter(enabled=True)
        req = self._get_request(**kwargs)
        return [ff for ff in flags if self._flag_is_active(ff, req)]
