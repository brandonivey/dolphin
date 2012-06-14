Settings
========

=====================
Functionality Options
=====================

DOLPHIN_USE_GIS
  Boolean. Use geolocation based flags. True enables this, False disables the option in the admin.

DOLPHIN_LIMIT_TO_SESSION
  Boolean. Limits a/b switching (max/current views and random) to the session of the user.
  This prevents the same user from seeing different flags on the site.

DOLPHIN_STORE_FLAGS
  Boolean. Store flag results for the entire request without recalculating them. Can speed up
  flag calculation


=============
Redis options
=============

DOLPHIN_REDIS_HOST
  String. The hostname the redis server is running at.

DOLPHIN_REDIS_PORT
  String. The port the redis server is running on.

DOLPHIN_REDIS_CONNECT
  Function. This allows you to specify your own function for connecting to redis. Expects a returned
  connection.

DOLPHIN_SET_NAME
  String. This setting changes the key name used for the set of flag names used in redis.

DOLPHIN_REDIS_TEST_DB
  The name of the database to use for testing redis.
