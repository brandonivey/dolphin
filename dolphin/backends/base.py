class Backend(object):
    """A base backend"""
    def is_active(self, key, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def delete(self, key, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")

    def active_flags(self, key, *args, **kwargs):
        raise NotImplementedError("Must be overriden by backend")
