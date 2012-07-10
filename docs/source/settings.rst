Settings
========

=====================
Functionality Options
=====================

.. _use_gis:

DOLPHIN_USE_GIS
---------------
  Boolean (Default True). Use geolocation based flags. True enables this, False disables the option in the admin.

.. _limit_to_session:
DOLPHIN_LIMIT_TO_SESSION
------------------------
  Boolean (Default True). Limits a/b switching (max/current views and random) to the session of the user.
  This prevents the same user from seeing different flags on the site.

.. _store_flags:
DOLPHIN_STORE_FLAGS
-------------------
  Boolean (Default True). Store flag results for the entire request without recalculating them. Can speed up
  flag calculation

.. _cache:
DOLPHIN_CACHE
-------------
  Boolean (Default True). Cache the get() queries in the django cache backend with prefix of dolphin

.. _autocreate_missing:
DOLPHIN_AUTOCREATE_MISSING
--------------------------
  Boolean (Default False). Create settings that are missing but used with is_active with enabled=False.

.. _test_flag:

DOLPHIN_TEST_FLAG
-----------------
  String (Default "dolphin_test"). The name of the flag for the dolphin_test url to return a valid page
  rather than a 404.

===============
Backend Options
===============

.. _backend:
DOLPHIN_BACKEND
---------------
  A dictionary that sets the backend options. The default is to use the DjangoBackend.

Default::

    {
        'BACKEND': 'dolphin.backends.djbackend.DjangoBackend'
        #The backend to use. should inherit from dolphin.backends.base.Backend
        #Builtin options are dolphin.backends.djbackend.DjangoBackend and
        #dolphin.backends.redisbackend.RedisBackend
    }


Redis Backend Defaults (must specify the BACKEND as RedisBackend)::

    {
        'BACKEND': 'dolphin.backends.redisbackend.RedisBackend', #the backend
        'DATABASE': 0, #the redis database to use
        'HOST' :'localhost', #the hostname to connect to
        'PORT': 6397, #the port to connect to
        'REDISENGINE': 'dolphin.backends.redisbackend.DefaultRedisEngine',
                       #the redis engine to use, subclass of redis.Redis.
                       #The default has a connection pool to connec to
                       #HOST and PORT.
        'TESTDB': 'featureflag_test'
    }
