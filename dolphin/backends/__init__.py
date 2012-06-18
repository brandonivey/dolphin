from .djbackend import DjangoBackend
try:
    import redis
    from .redisbackend import RedisBackend
except ImportError:
    #can't import redis
    pass
