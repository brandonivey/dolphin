from dolphin.models import FeatureFlag

class Backend(object):
    """A base backend"""
    def is_active(self, key, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def set_active(self, key, val, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def delete(self, key, **kwargs):
        raise NotImplementedError("Must be overriden by backend")


class DjangoBackend(Backend):
    """
    A basic django backend that tests if a flag is set
    No caching is done with this backend as of yet.
    """
    def is_active(self, key, **kwargs):
        try:
            f = FeatureFlag.objects.get(name=key)
            return f.enabled
        except FeatureFlag.DoesNotExist:
            return False

    def set_active(self, key, val, **kwargs):
        f, is_new = FeatureFlag.objects.get_or_create(name=key, defaults={'enabled':val})
        if not is_new and f.enabled != val:
            f.enabled = val
            f.save()

    def delete(self, key, **kwargs):
        FeatureFlag.objects.filter(name=key).delete()
