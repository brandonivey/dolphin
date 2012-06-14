from .manager import FlagManager
from dolphin import settings

if settings.DOLPHIN_USE_REDIS:
    from .backends import RedisBackend as backend
else:
    from .backends import DjangoBackend as backend

flipper = FlagManager(backend())
