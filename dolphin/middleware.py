from datetime import datetime
import threading

from django.conf import settings
from django.utils.encoding import smart_str

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
        self.local.clear()
        self.local['request'] = request

    def process_response(self, request, response):

        secure = getattr(settings, 'DOLPHIN_COOKIE_SECURE', False)
        dolphin_cookies = self.local.setdefault('dolphin_cookies', {})

        for cookie in dolphin_cookies:
            is_active = dolphin_cookies[cookie][0]
            flag_expire = dolphin_cookies[cookie][1]
            if flag_expire < datetime.now():
                flag_expire = 0
            #cookie name must be encoded since set_cookie doesn't like unicode values
            response.set_cookie(smart_str(cookie),
                                value=is_active,
                                max_age=datetime.strftime(flag_expire),
                                secure=secure)
        self.local.clear()
        return response

    def process_exception(self, request, exception):
        self.local.clear()
