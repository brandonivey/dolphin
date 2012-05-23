class FlagManager(object):
    def __init__(self, backend):
        self.backend = backend

    def is_active(self, key, **kwargs):
        return self.backend.is_active(key, **kwargs)

    def set_active(self, key, val, **kwargs):
        return self.backend.set_active(key, val, **kwargs)

    def delete(self, key, **kwargs):
        return self.backend.delete(key, **kwargs)
