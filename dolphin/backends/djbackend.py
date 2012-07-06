import copy

from django.db.models import F
from django.core.cache import cache

from dolphin import settings
from dolphin.models import FeatureFlag
from dolphin.middleware import LocalStoreMiddleware
from dolphin.utils import DefaultDict
from .utils import Schema, cache_key
from .base import Backend


class DjangoBackend(Backend):
    """
    A basic django backend that tests if a flag is set
    The only caching done with this backend is a per-request
    cache for each flag if DOLPHIN_STORE_FLAGS is True.
    """

    def _check_maxb(self, flag, request):
        maxt = flag.maximum_b_tests
        if flag.current_b_tests >= flag.maximum_b_tests:
            return False

        FeatureFlag.objects.filter(id=flag.id).update(current_b_tests=F('current_b_tests')+1)
        if settings.DOLPHIN_CACHE:
            cache.delete(cache_key(flag.name))
        return True

    def _get_flag(self, key):
        if settings.DOLPHIN_CACHE:
            ff = cache.get(cache_key(key))
            if ff is not None:
                return DefaultDict(Schema().parse(ff))

        try:
            ff = FeatureFlag.objects.get(name=key)
        except FeatureFlag.DoesNotExist:
            if not settings.DOLPHIN_AUTOCREATE_MISSING:
                return None
            ff = FeatureFlag.objects.create(name=key, enabled=False)

        if settings.DOLPHIN_CACHE:
            cache.set(cache_key(key), Schema().serialize(copy.copy(ff.__dict__)))

        return ff

    def delete(self, key, *args, **kwargs):
        FeatureFlag.objects.filter(name=key).delete()
        #just delete the store and make them recalculate
        del LocalStoreMiddleware.local['flags']

    def all_flags(self, *args, **kwargs):
        return FeatureFlag.objects.all()
