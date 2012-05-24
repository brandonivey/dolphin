import re

from django.utils.unittest import TestCase
from django.template import Context, Template

from dolphin.models import FeatureFlag

class TemplateTagTest(TestCase):
    def setUp(self):
        FeatureFlag.objects.create(name="testing_enabled", enabled=True)
        FeatureFlag.objects.create(name="testing_disabled", enabled=False)

    def tearDown(self):
        FeatureFlag.objects.all().delete()

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
        {% ifactive testing_enabled %}
        Test
        {% endifactive %}
        """

        expected_resp = "Test"
        self.check_res(text, expected_resp)

    def test_ifactive_disabled(self):
        text = r"""
        {% load dolphin_tags %}
        {% ifactive testing_disabled %}
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
        {% ifactive testing_missing %}
        Test4
        {% else %}
        Test5
        {% endifactive %}
        """
        expected_resp = "Test5"
        self.check_res(text, expected_resp)
