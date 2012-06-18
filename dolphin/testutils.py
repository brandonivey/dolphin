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
    #taken and simplified from django loaddata command

    # Keep a count of the installed objects and fixtures
    fixture_count = 0
    loaded_object_count = 0
    fixture_object_count = 0
    models = set()

    humanize = lambda dirname: "'%s'" % dirname if dirname else 'absolute path'

    # Get a cursor (even though we don't need one yet). This has
    # the side effect of initializing the test database (if
    # it isn't already initialized).

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

    try:
        for fixture_label in fixture_labels:
            parts = fixture_label.split('.')

            if len(parts) == 1:
                fixture_name = parts[0]
                formats = serializers.get_public_serializer_formats()
            else:
                fixture_name, format = '.'.join(parts[:-1]), parts[-1]
                if format in serializers.get_public_serializer_formats():
                    formats = [format]
                else:
                    formats = []

            if os.path.isabs(fixture_name):
                fixture_dirs = [fixture_name]
            else:
                fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

            for fixture_dir in fixture_dirs:
                label_found = False
                for format in formats:
                    file_name = '.'.join(
                        p for p in [
                            fixture_name, format
                        ]
                        if p
                    )

                    full_path = os.path.join(fixture_dir, file_name)
                    try:
                        fixture = open(full_path, 'r')
                    except IOError:
                        pass
                    else:
                        try:
                            if label_found:
                                stderr.write("Multiple fixtures named '%s' in %s. Aborting.\n" %
                                    (fixture_name, humanize(fixture_dir)))
                                return

                            fixture_count += 1
                            objects_in_fixture = 0
                            loaded_objects_in_fixture = 0

                            objects = sj.load(fixture)
                            for obj in objects:
                                objects_in_fixture += 1

                                if obj['model'] == 'dolphin.featureflag':
                                    fields = obj['fields']
                                    key = fields['name']
                                    backend.update(key, fields)

                            loaded_object_count += loaded_objects_in_fixture
                            fixture_object_count += objects_in_fixture
                            label_found = True
                        finally:
                            fixture.close()

                        # If the fixture we loaded contains 0 objects, assume that an
                        # error was encountered during fixture loading.
                        if objects_in_fixture == 0:
                            return


    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception:
        raise


