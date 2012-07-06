import redis

from django.conf import settings as django_settings

from .base import Backend
from .utils import Schema
from dolphin import settings
from dolphin.utils import DefaultDict


class DefaultBackend(redis.Redis):
    def __init__(self, database=0):
        host = settings.DOLPHIN_REDIS_HOST
        port = settings.DOLPHIN_REDIS_PORT

        if not hasattr(DefaultBackend, '_connection_pools'):
            DefaultBackend._connection_pools = {}

        if database not in self._connection_pools:
            self._connection_pools[database] = redis.ConnectionPool(host=host, port=port, db=database)

        super(DefaultBackend, self).__init__(connection_pool=self._connection_pools[database])


class RedisBackend(Backend):
    def __init__(self, database=0):
        self.database = database

        self.redisbackend = getattr(django_settings, 'DOLPHIN_REDIS_BACKEND', DefaultBackend)

        super(RedisBackend, self).__init__()

    def _get_backend(self):
        return self.redisbackend(database=self.database)

    def _get_redis_val(self, key):
        r = self._get_backend()
        val = r.hgetall(key)
        if val is None or val == {}:
            return None

        return DefaultDict(Schema().parse(val))

    def _get_flag(self, key):
        val = self._get_redis_val(key)
        if val is None and settings.DOLPHIN_AUTOCREATE_MISSING:
            #create the missing key and return the object
            val = {'name':key, 'enabled':False}
            self.update(key, val)
            return DefaultDict(Schema().parse(val))
        return val

    def _check_maxb(self, flag, request):
        r = self._get_backend()
        maxt = int(flag.maximum_b_tests)
        current_b_tests = int(flag.current_b_tests) if flag.current_b_tests is not None else 0
        if current_b_tests >= maxt:
            return False

        return r.hincrby(flag.name, 'current_b_tests', 1) <=  maxt

    def get_names(self):
        r = self._get_backend()
        setname = settings.DOLPHIN_SET_NAME
        flags = r.smembers(setname)
        return flags

    def update(self, key, d):
        d = Schema().serialize(d)
        r = self._get_backend()
        if 'name' not in d:
            d['name'] = key
        r.hmset(key, d)
        setname = settings.DOLPHIN_SET_NAME
        r.sadd(setname, key)

    def all_flags(self, *args, **kwargs):
        return [self._get_redis_val(key) for key in self.get_names()]
