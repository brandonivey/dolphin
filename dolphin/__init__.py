__version__ = '0.1.3'

from .manager import FlagManager
from dolphin import settings

if settings.DOLPHIN_USE_REDIS:
    from .backends import RedisBackend as Backend
    database = settings.DOLPHIN_REDIS_DB
    backend = Backend(database=database)
else:
    from .backends import DjangoBackend as Backend
    backend = Backend()

flipper = FlagManager(backend)
