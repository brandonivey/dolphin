import copy

from django.db.models import F
from django.conf import settings as django_settings
from django.core.cache import cache

from dolphin import settings
from dolphin.models import FeatureFlag
from dolphin.middleware import LocalStoreMiddleware
from dolphin.utils import DefaultDict
from .utils import Schema, cache_key
from .base import Backend as BaseBackend

#Utilize a more granular caching timeout value for queries that involve the sites many to many field
DOLPHIN_SITES_CACHE_TIMEOUT = getattr(settings, 'DOLPHIN_SITES_CACHE_TIMEOUT', 1)

class DjangoBackend(BaseBackend):
    """
    A basic django backend that tests if a flag is set
    The only caching done with this backend is a per-request
    cache for each flag if DOLPHIN_STORE_FLAGS is True.
    """

    def _check_maxb(self, flag):
        maxt = flag.maximum_b_tests
        if flag.current_b_tests >= flag.maximum_b_tests:
            return False

        FeatureFlag.objects.filter(id=flag.id).update(current_b_tests=F('current_b_tests')+1)
        if settings.DOLPHIN_CACHE:
            cache.delete(cache_key(flag.name))
        return True

    def _enabled_for_site(self, flag):
        """ Check to see if this flag is enabled for this site.
            Cache the results for DOLPHIN_SITES_CACHE_TIMEOUT seconds.
        """
        sites_cache_key = "%s%s" % (cache_key(flag.name), django_settings.SITE_ID)
        if settings.DOLPHIN_CACHE:
            site_enabled = cache.get(sites_cache_key)
            if site_enabled is not None:
                return site_enabled

        if not flag.enable_for_sites and not flag.disable_for_sites:
            return True

        if flag.enable_for_sites:
            site_enabled = FeatureFlag.objects.filter(sites=django_settings.SITE_ID).exists()
        else:
            site_enabled = not FeatureFlag.objects.filter(sites=django_settings.SITE_ID).exists()

        if settings.DOLPHIN_CACHE:
            cache.set(sites_cache_key, site_enabled,  DOLPHIN_SITES_CACHE_TIMEOUT)

        return site_enabled

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
