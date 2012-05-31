import re

from django.contrib.auth.models import User
from django.template import Context, Template

from dolphin.middleware import LocalStoreMiddleware
from dolphin.tests.flipper import BaseTest

class ActiveTagTest(BaseTest):
    fixtures = ['base_flags.json']

    def check_res(self, text, expected):
        t = Template(text)
        c = Context()

        res = t.render(c)
        res = ' '.join(re.findall("[a-zA-Z0-9]+", res)) #strip \n and spaces
        self.assertEqual(res,
                         expected)

    def test_ifactive_enabled(self):
        text = r"""
        {% load dolphin_tags %}
        {% ifactive "enabled" %}
        Test
        {% endifactive %}
        """

        expected_resp = "Test"
        self.check_res(text, expected_resp)

    def test_ifactive_disabled(self):
        text = r"""
        {% load dolphin_tags %}
        {% ifactive "testing_disabled" %}
        Test2
        {% else %}
        Test3
        {% endifactive %}
        """
        expected_resp = "Test3"
        self.check_res(text, expected_resp)

    def test_ifactive_missing(self):
        text = r"""
        {% load dolphin_tags %}
        {% ifactive "testing_missing" %}
        Test4
        {% else %}
        Test5
        {% endifactive %}
        """
        expected_resp = "Test5"
        self.check_res(text, expected_resp)

class FlagListTest(BaseTest):
    fixtures = ['users.json', 'user_flags.json', 'base_flags.json']

    def clear(self):
        LocalStoreMiddleware.local.clear()

    def _fake_request(self):
        req = type("Request", (object,), {})()
        return req

    def test_active_flag_list(self):
        text = r"""{% load dolphin_tags %}{% active_tags %}"""
        t = Template(text)
        c = Context()

        res = t.render(c)
        self.assertEqual(res,
                         "enabled")

    def test_active_flag_list_user(self):
        text = r"""{% load dolphin_tags %}{% active_tags %}"""
        req = self._fake_request()
        req.user = User.objects.get(username="registered")
        c = Context({'request':req})
        t = Template(text)
        res = t.render(c)
        #test a registered user that is in a selected_users flag
        self.assertEqual(res,
                         "enabled,registered_only,selected_users")

        self.clear()
        req.user = User.objects.get(username='staff')
        c = Context({'request':req})
        t = Template(text)
        res = t.render(c)
        #test a staff user that is not in the selected_users flag
        self.assertEqual(res,
                         "enabled,registered_only,staff_only")
