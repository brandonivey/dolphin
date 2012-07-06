from dolphin import settings
if settings.DOLPHIN_USE_REDIS:
    from .redisbackend import RedisBackend
else:
    from .djbackend import DjangoBackend
