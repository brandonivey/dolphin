from contextlib import contextmanager
from .middleware import LocalStoreMiddleware


@contextmanager
def set_active(key, val):
    """Allows a flag to be switched to enabled"""
    overrides = LocalStoreMiddleware.local.setdefault('overrides', {})
    overrides[key] = val
    yield
    del overrides[key]
