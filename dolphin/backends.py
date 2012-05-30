from .models import FeatureFlag
from .middleware import RequestStoreMiddleware
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
        return RequestStoreMiddleware.request()

    def _in_circle(self, ff, lat, lon):
        dist = calc_dist(ff.center_lat, ff.center_lon, lat, lon)
        if dist <= ff.radius:
            return True
        return False

    def _flag_is_active(self, ff, request):
        if not ff.enabled:
            return False

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

        if ff.enable_geo:
            #distance based
            x = get_geoip_coords(get_ip(request))
            if x is None:
                enabled = False
            else:
                enabled = enabled and self._in_circle(ff, x[0], x[1])

        return enabled

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
        if not registered:
            return flags.filter(registered_only=False, staff_only=False, limit_to_users=False)

        return [ff for ff in flags if self._flag_is_active(ff, req)]
