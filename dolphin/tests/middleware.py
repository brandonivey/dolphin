from django.test import TestCase

from dolphin.middleware import LocalStoreMiddleware

class RequestStoreMiddlewareTest(TestCase):
    def test_middleware(self):
        req = "Test fake request"
        m = LocalStoreMiddleware()
        m.process_request(req)
        self.assertEquals(m.request(), req)
