import datetime
import random
import time
import pytz

from django.db.models import F
from django.utils.datastructures import SortedDict
from django.conf import settings

from .models import FeatureFlag
from .middleware import LocalStoreMiddleware
from .utils import calc_dist, get_ip, get_geoip_coords

class Backend(object):
    """A base backend"""
    def is_active(self, key, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def set_active(self, key, val, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def delete(self, key, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")


class DjangoBackend(Backend):
    """
    A basic django backend that tests if a flag is set
    No caching is done with this backend as of yet.
    """
    def _get_request(self, **kwargs):
        if kwargs.get('request', None) is not None:
            return kwargs['request']
        return LocalStoreMiddleware.request()

    def _in_circle(self, ff, lat, lon):
        dist = calc_dist(ff.center_lat, ff.center_lon, lat, lon)
        if dist <= ff.radius:
            return True
        return False

    def _once_per_req(self, name, key, func):
        d = LocalStoreMiddleware.local.setdefault(name, {})

        if key in d:
            return d[key]

        val = func()
        d[key] = val
        return val

    def _flag_key(self, ff, request):
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
        key = self._flag_key(ff, request)
        flags = LocalStoreMiddleware.local.setdefault('flags', {})
        store_flags = getattr(settings, 'DOLPHIN_STORE_FLAGS', True)

        if store_flags and key in flags:
            return flags[key]

        def store(val):
            if store_flags: flags[key] = val
            return val

        if not ff.enabled:
            return store(False)

        enabled = True
        if ff.registered_only or ff.limit_to_users or ff.staff_only:
            #user based flag
            if not request: enabled = False #TODO error here?
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

        if ff.is_ab_test:
            if ff.random:
                #doing this so that the random key is only calculated once per request
                def rand_bool():
                    random.seed(time.time())
                    return bool(random.randrange(0, 2))

                enabled = enabled and self._once_per_req('random', ff.name, rand_bool)

            if ff.b_test_start:
                if ff.b_test_start.tzinfo is not None:
                    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
                else:
                    now = datetime.datetime.now()
                enabled = enabled and now >= ff.b_test_start

            if ff.b_test_end:
                if ff.b_test_end.tzinfo is not None:
                    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
                else:
                    now = datetime.datetime.now()
                enabled = enabled and now <= ff.b_test_end

            if ff.maximum_b_tests:
                #TODO - is this worth becoming atomic and locking?
                def maxb():
                    maxt = ff.maximum_b_tests
                    if ff.current_b_tests >= ff.maximum_b_tests:
                        return False

                    if enabled:
                        FeatureFlag.objects.filter(id=ff.id).update(current_b_tests=F('current_b_tests')+1)
                    return True
                enabled = enabled and self._once_per_req('maxb', ff.name, maxb)

        return store(enabled)

    def is_active(self, key, *args, **kwargs):
        try:
            ff = FeatureFlag.objects.get(name=key)
            req = self._get_request(**kwargs)
            return self._flag_is_active(ff, req)

        except FeatureFlag.DoesNotExist:
            return False

    def set_active(self, key, val, *args, **kwargs):
        f, is_new = FeatureFlag.objects.get_or_create(name=key, defaults={'enabled':val})
        if not is_new and f.enabled != val:
            f.enabled = val
            f.save()

    def delete(self, key, *args, **kwargs):
        FeatureFlag.objects.filter(name=key).delete()

    def active_flags(self, *args, **kwargs):
        flags = FeatureFlag.objects.filter(enabled=True)
        req = self._get_request(**kwargs)
        registered = req and req.user.is_authenticated()
        return [ff for ff in flags if self._flag_is_active(ff, req)]
