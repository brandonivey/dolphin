Testing
=======

A test app is included for testing dolphin. It by default uses the sqlite3 backend.
With south and mock installed, and DJANGO_SETTINGS_MODULE=testapp,
running tests should be as simple as::

    python manage.py test dolphin
