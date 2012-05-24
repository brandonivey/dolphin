class FlagManager(object):
    def __init__(self, backend):
        self.backend = backend

    def is_active(self, key, *args, **kwargs):
        return self.backend.is_active(key, *args, **kwargs)

    def set_active(self, key, val, *args, **kwargs):
        return self.backend.set_active(key, val, *args, **kwargs)

    def delete(self, key, *args, **kwargs):
        return self.backend.delete(key, *args, **kwargs)
