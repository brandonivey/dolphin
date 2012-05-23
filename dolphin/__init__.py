from .manager import FlagManager
from .backends import DjangoBackend

flipper = FlagManager(DjangoBackend())
