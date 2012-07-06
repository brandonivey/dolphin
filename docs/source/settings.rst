Settings
========

=====================
Functionality Options
=====================

DOLPHIN_USE_GIS
  Boolean (Default True). Use geolocation based flags. True enables this, False disables the option in the admin.

DOLPHIN_LIMIT_TO_SESSION
  Boolean (Default True). Limits a/b switching (max/current views and random) to the session of the user.
  This prevents the same user from seeing different flags on the site.

DOLPHIN_STORE_FLAGS
  Boolean (Default True). Store flag results for the entire request without recalculating them. Can speed up
  flag calculation

DOLPHIN_CACHE
  Boolean (Default True). Cache the get() queries in the django cache backend with prefix of dolphin

DOLPHIN_AUTOCREATE_MISSING
  Boolean (Default False). Create settings that are missing but used with is_active with enabled=False.

DOLPHIN_TEST_FLAG
  String (Default "dolphin_test"). The name of the flag for the dolphin_test url to return a valid page
  rather than a 404.

=============
Redis options
=============

DOLPHIN_USE_REDIS
  Boolean (Default False). Enable redis, or if disabled use the django backend.

DOLPHIN_REDIS_HOST
  String (Default 'localhost'). The hostname the redis server is running at.

DOLPHIN_REDIS_PORT
  Int (Default 6379). The port the redis server is running on.

DOLPHIN_DB
  String (Default 0). The database to use. Defaults to the redis default.

DOLPHIN_REDIS_BACKEND
  redis.Redis class. This allows you to customize the redis class being instantiated.
  The class must take a database argument. The default backend uses a connection pool to connect.
  
DOLPHIN_SET_NAME
  String (Default featureflags). This setting changes the key name used for the set of flag names used in redis.

DOLPHIN_REDIS_TEST_DB
  String (Default featureflag_test). The name of the database to use for testing redis.
