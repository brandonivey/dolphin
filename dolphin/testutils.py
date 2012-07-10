import os
from sys import stdout, stderr

from contextlib import contextmanager
from django.db.models import get_apps
from django.utils import simplejson as sj
from django.core import serializers
from django.conf import settings
from django.utils.itercompat import product

from .middleware import LocalStoreMiddleware

@contextmanager
def set_active(key, val):
    """Allows a flag to be switched to enabled"""
    overrides = LocalStoreMiddleware.local.setdefault('overrides', {})
    overrides[key] = val
    yield
    del overrides[key]


def load_redis_fixtures(fixture_labels, backend):
    # Keep a count of the installed objects and fixtures
    # changes marked by # + or # - and endchanges for +

    # - removed intro code

    fixture_count = 0
    loaded_object_count = 0
    fixture_object_count = 0
    models = set()

    humanize = lambda dirname: "'%s'" % dirname if dirname else 'absolute path'

    # - removed cursor code, compression types

    app_module_paths = []
    for app in get_apps():
        if hasattr(app, '__path__'):
            # It's a 'models/' subpackage
            for path in app.__path__:
                app_module_paths.append(path)
        else:
            # It's a models.py module
            app_module_paths.append(app.__file__)

    app_fixtures = [os.path.join(os.path.dirname(path), 'fixtures') for path in app_module_paths]

    # - remove try, connection constraint
    for fixture_label in fixture_labels:
        parts = fixture_label.split('.')

        if len(parts) == 1: # - remove compression
            fixture_name = parts[0]
            formats = serializers.get_public_serializer_formats()
        else:
            fixture_name, format = '.'.join(parts[:-1]), parts[-1]
            if format in serializers.get_public_serializer_formats():
                formats = [format]
            else:
                formats = []

        # - remove formats
        if os.path.isabs(fixture_name):
            fixture_dirs = [fixture_name]
        else:
            fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

        for fixture_dir in fixture_dirs:
            # - remove verbosity
            label_found = False
            # - remove compression formats, verbosity
            for format in formats:
                file_name = '.'.join(
                    p for p in [
                        fixture_name, format
                    ]
                    if p
                )

                full_path = os.path.join(fixture_dir, file_name)
                # - remove compression method
                try:
                    fixture = open(full_path, 'r')
                except IOError:
                    # - remove verbosity
                    pass
                else:
                    try:
                        if label_found:
                            stderr.write("Multiple fixtures named '%s' in %s. Aborting.\n" %
                                (fixture_name, humanize(fixture_dir)))
                            # - remove commit
                            return

                        fixture_count += 1
                        objects_in_fixture = 0
                        loaded_objects_in_fixture = 0
                        # - remove verbosity

                        # - remove generalized loading of fixture
                        # + customized loading of fixture
                        objects = sj.load(fixture)
                        for obj in objects:
                            objects_in_fixture += 1

                            #begin customization
                            if obj['model'] == 'dolphin.featureflag':
                                fields = obj['fields']
                                key = fields['name']
                                backend.update(key, fields)
                        #endchanges

                        loaded_object_count += loaded_objects_in_fixture
                        fixture_object_count += objects_in_fixture
                        label_found = True
                    finally:
                        fixture.close()

                    # If the fixture we loaded contains 0 objects, assume that an
                    # error was encountered during fixture loading.
                    if objects_in_fixture == 0:
                        # - remove verbosity
                        return

        # - remove everything else
