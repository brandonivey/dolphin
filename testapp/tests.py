import mock

from django.test.client import Client

from dolphin.middleware import LocalStoreMiddleware
from dolphin.tests.flipper import BaseTest
from dolphin import flipper

class SessionTest(BaseTest):
    fixtures = ['ab_flags.json']

    def test_max_session(self):
        """Tests that max stores the flag properly in the request"""
        c = Client()
        for i in xrange(0, 5):
            resp = c.get('/flag_is_active/max/')
            self.assertEquals(resp.content, "True")
            LocalStoreMiddleware.local.clear()

        c = Client()
        resp = c.get('/flag_is_active/max/')
        self.assertEquals(resp.content, "True")

    @mock.patch('random.randrange')
    def test_random(self, randrange):
        """Tests that the random flag is working correctly"""
        c = Client()
        randrange.return_value = 1
        resp = c.get('/flag_is_active/ab_random/')
        self.assertEquals(resp.content, "True")

        LocalStoreMiddleware.local.clear()
        randrange.return_value = 0
        self.assertFalse(flipper.is_active('ab_random'))
        resp = c.get('/flag_is_active/ab_random/')
        self.assertEquals(resp.content, "True")
