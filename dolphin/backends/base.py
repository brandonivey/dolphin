import datetime
from decimal import Decimal
import pytz
import random
import time

from django.utils.datastructures import SortedDict

from dolphin import settings
from dolphin.middleware import LocalStoreMiddleware
from dolphin.utils import get_ip, get_geoip_coords, calc_dist

class Backend(object):
    """A base backend"""
    def __init__(self, **kwargs):
        self.backend_settings = kwargs

    def _check_maxb(self, flag, request):
        raise NotImplementedError("Must be overriden by backend")

    def _get_flag(self, key):
        raise NotImplementedError("Must be overriden by backend")

    def delete(self, key, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def all_flags(self):
        raise NotImplementedError("Must be overriden by backend")

    def _get_request(self, **kwargs):
        if kwargs.get('request', None) is not None:
            return kwargs['request']
        return LocalStoreMiddleware.request()

    def _in_circle(self, ff, lat, lon):
        if isinstance(ff, (tuple, list)):
            f_lat = ff[0]
            f_lon = ff[1]
        else:
            f_lat = ff.center.latitude
            f_lon = ff.center.longitude
        dist = calc_dist(float(f_lat), float(f_lon), lat, lon)
        return dist <= ff.radius

    def _check_percent(self, flag, request):
        return False if flag.percent is 0 else random.uniform(0, 100) <= flag.percent

    def _limit(self, name, flag, func, request):
        """
        Limits the option to once per request
        and once per session if it's enabled (requires the session middleware)
        """
        if hasattr(request, 'session') and settings.DOLPHIN_LIMIT_TO_SESSION:
            d = request.session.setdefault(name, {})
        else:
            d = LocalStoreMiddleware.local.setdefault(name, {})

        if flag.name not in d:
            d[flag.name] = func(flag, request)
        return d[flag.name]

    def set_cookie(self, request, flag_name, active=True):
        """
        Set a flag value in dolphin's local store that will
        be set as a cookie in the middleware's process response function.
        """
        cookie_prefix = getattr(settings, 'DOLPHIN_COOKIE', 'dolphin_%s')
        cookie = cookie_prefix % flag_name
        dolphin_cookies = LocalStoreMiddleware.local.setdefault('dolphin_cookies', {})
        dolphin_cookies[cookie] = active

    def is_active(self, key, *args, **kwargs):
        """
        Checks if a flag exists and is active
        """
        overrides = LocalStoreMiddleware.local.setdefault('overrides', {})
        if key in overrides:
            return overrides[key]
        flag = self._get_flag(key)
        request = self._get_request(**kwargs)

        #If there is a cookie for this flag, use it
        if hasattr(request, 'COOKIES'):
            cookie_prefix = getattr(settings, 'DOLPHIN_COOKIE', 'dolphin_%s')
            cookie = cookie_prefix % flag.name
            if cookie in request.COOKIES:
                return request.COOKIES[cookie]
        return False if flag is None else self._flag_is_active(flag, request)

    def active_flags(self, *args, **kwargs):
        """Returns active flags for the current request"""
        request = self._get_request(**kwargs)
        return [flag for flag in self.all_flags() if self._flag_is_active(flag, request)]

    def _in_group(self, flag, request):
        """Checks if the request's users is in the group specified by flag.group(_id)"""
        if isinstance(flag.group_id, int):
            group_id = flag.group_id
        else:
            group_id = flag.group # for the cache objects and redis
        return request.user.groups.filter(id=group_id).exists()

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


    def _flag_is_active(self, flag, request):
        """
        Checks the flag to see if it should be enabled or not.
        Encompases A/B tests, regional, and user based flags as well.
        Will only calculate random and max flags once per request.
        Will store flags for the request if DOLPHIN_STORE_FLAGS is True (default).
        """

        key = self._flag_key(flag, request)
        flags = LocalStoreMiddleware.local.setdefault('flags', {})
        store_flags = settings.DOLPHIN_STORE_FLAGS

        if store_flags and key in flags:
            return flags[key]

        def store(val):
            """quick wrapper to store the flag results if it needs to"""
            if store_flags: flags[key] = val
            return val

        if not flag.enabled:
            return store(False)

        enabled = True
        if flag.registered_only or flag.limit_to_group or flag.staff_only:
            #user based flag
            if not request: enabled = False
            elif not request.user.is_authenticated():
                enabled = False
            else:
                if flag.limit_to_group:
                    enabled = enabled and self._in_group(flag, request)
                if flag.staff_only:
                    enabled = enabled and request.user.is_staff
                if flag.registered_only:
                    enabled = enabled and True

        if enabled == False:
            return store(enabled)

        if flag.enable_geo:
            #distance based
            x = get_geoip_coords(get_ip(request))
            if x is None or flag.center is None:
                enabled = False
            else:
                enabled = enabled and self._in_circle(flag, x[0], x[1])

        if enabled == False:
            return store(enabled)

        #A/B flags
        if flag.random:
            #doing this so that the random key is only calculated once per request
            def rand_bool(flag, request):
                random.seed(time.time())
                return bool(random.randrange(0, 2))

            enabled = enabled and self._limit('random', flag, rand_bool, request)

        if flag.b_test_start:
            #start date
            if flag.b_test_start.tzinfo is not None:
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            else:
                now = datetime.datetime.now()
            enabled = enabled and now >= flag.b_test_start

        if flag.b_test_end:
            #end date
            if flag.b_test_end.tzinfo is not None:
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
            else:
                now = datetime.datetime.now()
            enabled = enabled and now <= flag.b_test_end

        if flag.maximum_b_tests:
            #max B tests
            enabled = enabled and self._limit('maxb', flag, self._check_maxb, request)

        percent_active = self._limit('percent', flag, self._check_percent, request)

        if percent_active and flag.percent != 100:
           #100 percent flips the feature on and roll out mode off,
           #so there is no need for storing it in a cookie.
           self.set_cookie(request, flag.name, percent_active)

        enabled = enabled and percent_active

        return store(enabled)
