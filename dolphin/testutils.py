from contextlib import contextmanager
from . import flipper

@contextmanager
def set_active(key, val):
    active = flipper.is_active(key)
    flipper.set_active(key, val)
    yield
    flipper.set_active(key, active)
