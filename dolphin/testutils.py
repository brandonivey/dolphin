from contextlib import contextmanager
from . import flipper
from .middleware import LocalStoreMiddleware

@contextmanager
def set_active(key, val):
    active = flipper.is_active(key)
    flipper.set_active(key, val)
    del LocalStoreMiddleware.local['flags']
    yield
    del LocalStoreMiddleware.local['flags']
    flipper.set_active(key, active)
