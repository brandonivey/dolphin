from django.conf import settings as django_settings

DOLPHIN_USE_REDIS = getattr(django_settings, 'DOLPHIN_USE_REDIS', False)
DOLPHIN_LIMIT_TO_SESSION = getattr(django_settings, 'DOLPHIN_LIMIT_TO_SESSION', True)
DOLPHIN_STORE_FLAGS = getattr(django_settings, 'DOLPHIN_STORE_FLAGS', True)
DOLPHIN_USE_GIS = getattr(django_settings, 'DOLPHIN_USE_GIS', True)
DOLPHIN_CACHE = getattr(django_settings, 'DOLPHIN_CACHE', True)

DOLPHIN_REDIS_HOST = getattr(django_settings, 'DOLPHIN_REDIS_HOST', 'localhost')
DOLPHIN_REDIS_PORT = getattr(django_settings, 'DOLPHIN_REDIS_PORT', 6379)
DOLPHIN_SET_NAME = getattr(django_settings, 'DOLPHIN_SET_NAME', 'featureflags')
DOLPHIN_REDIS_TEST_DB = getattr(django_settings, "DOLPHIN_REDIS_TEST_DB", 'featureflag_test')
