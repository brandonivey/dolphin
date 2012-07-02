from setuptools import setup, find_packages
import sys, os, re

module_file = open("dolphin/__init__.py").read()
metadata = dict(re.findall("^__([a-z]*)__\s*=\s*'([^']*)'", module_file))

setup(name='dolphin',
      version=metadata['version'],
      description="A feature flagging library for Django",
      long_description="""A feature flagging and A/B testing library for Django""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='feature-flipping django',
      author='Jeremy Self',
      author_email='jeremy.self@coxinc.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pytz', 'mock'
      ],
      entry_points="",
      )
