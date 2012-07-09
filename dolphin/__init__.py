__version__ = '0.1.4'

from .manager import FlagManager
from dolphin import settings
from dolphin.utils import import_class

backend_settings = settings.DOLPHIN_BACKEND
backend = import_class(backend_settings['BACKEND'])(**backend_settings)

flipper = FlagManager(backend)
