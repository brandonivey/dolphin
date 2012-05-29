from django.test import TestCase

from dolphin.middleware import RequestStoreMiddleware

class TestRequestStoreMiddleware(TestCase):
    def test_middleware(self):
        req = "Test fake request"
        m = RequestStoreMiddleware()
        m.process_request(req)
        self.assertEquals(m.request(), req)
