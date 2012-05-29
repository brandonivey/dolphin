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
        if 'request' in kwargs:
            return kwargs['request']
        return RequestStoreMiddleware.request

    def is_active(self, key, *args, **kwargs):
        try:
            f = FeatureFlag.objects.get(name=key)
            if not f.enabled:
                return False

            if f.registered_only or f.limit_to_users or f.staff_only:
                #user based flag
                request = self._get_request(**kwargs)
                if not request: return False #TODO error here?
                if not request.user.is_authenticated():
                    return False
                if f.staff_only:
                    return request.user.is_staff
                if f.limit_to_users:
                    return bool(f.users.filter(id=request.user.id).exists())
                if f.registered_only:
                    return True

            return True

        except FeatureFlag.DoesNotExist:
            return False

    def set_active(self, key, val, *args, **kwargs):
        f, is_new = FeatureFlag.objects.get_or_create(name=key, defaults={'enabled':val})
        if not is_new and f.enabled != val:
            f.enabled = val
            f.save()

    def delete(self, key, *args, **kwargs):
        FeatureFlag.objects.filter(name=key).delete()
