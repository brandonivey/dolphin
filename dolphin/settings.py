from django.conf import settings as django_settings

default_backend = {
    'BACKEND': 'dolphin.backends.djbackend.DjangoBackend'
}

DOLPHIN_BACKEND = getattr(django_settings, 'DOLPHIN_BACKEND', default_backend)

#Turn caching back on when finihed with testing.
DOLPHIN_LIMIT_TO_SESSION = getattr(django_settings, 'DOLPHIN_LIMIT_TO_SESSION', False)
DOLPHIN_STORE_FLAGS = getattr(django_settings, 'DOLPHIN_STORE_FLAGS', False)
DOLPHIN_USE_GIS = getattr(django_settings, 'DOLPHIN_USE_GIS', True)
DOLPHIN_CACHE = getattr(django_settings, 'DOLPHIN_CACHE', False)
DOLPHIN_AUTOCREATE_MISSING = getattr(django_settings, 'DOLPHIN_AUTOCREATE_MISSING', False)

DOLPHIN_TEST_FLAG = getattr(django_settings, "DOLPHIN_TEST_FLAG", "dolphin_test")
