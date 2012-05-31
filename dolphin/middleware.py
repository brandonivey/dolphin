import threading

class LocalStore(threading.local):
    def __setitem__(self, key, val):
        self.__dict__[key] = val

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        if key in self.__dict__:
            del self.__dict__[key]

    def clear(self):
        self.__dict__.clear()

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default

    def setdefault(self, key, value):
        if key not in self.__dict__:
            self.__dict__[key] = value
        return self.__dict__[key]


class LocalStoreMiddleware(object):
    local = LocalStore()
    """Stores the request object for making it so that the template tags/etc don't
    have to pass the request object in"""

    @staticmethod
    def request():
        return LocalStoreMiddleware.local.get('request')

    def clear(self):
        self.local.clear()

    def process_request(self, request):
        self.local['request'] = request

    def process_response(self, request, response):
        self.clear()
        return response

    def process_exception(self, request, exception):
        self.clear()
