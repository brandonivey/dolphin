from .models import FeatureFlag
from .middleware import RequestStoreMiddleware

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

    def _flag_is_active(self, ff, request):
        if not ff.enabled:
            return False

        if ff.registered_only or ff.limit_to_users or ff.staff_only:
            #user based flag
            if not request: return False #TODO error here?
            if not request.user.is_authenticated():
                return False
            if ff.limit_to_users:
                return bool(ff.users.filter(id=request.user.id).exists())
            if ff.staff_only:
                return request.user.is_staff
            if ff.registered_only:
                return True

        return True

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
