import threading

class RequestStoreMiddleware(object):
    """Stores the request object for making it so that the template tags/etc don't
    have to pass the request object in"""
    def __init__(self):
        if not hasattr(self, "local"):
            self.local = threading.local()

    @property
    def request(self):
        return self.local.__dict__.get('request', None)

    def clear(self):
        self.local.__dict__.clear()

    def process_request(self, request):
        self.local.__dict__['request'] = request

    def process_response(self, request, response):
        self.clear()
        return response

    def process_exception(self, request, exception):
        self.clear()
