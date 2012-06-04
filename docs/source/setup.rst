Setup
=====

1. Add "dolphin.middleware.LocalStoreMiddleware" to your MIDDLEWARE_CLASSES. 
   This allows per-request random testing and per-request caching.
2. Add "dolphin" to INSTALLED_APPS
3. Ensure that REMOTE_ADDR is pointing to the correct IP address. If not,
   you will have to otherwise patch dolphin.utils.get_ip to use geoip.
4. Load database table using manage.py, either via syncdb or migrate dolphin if using south.
5. If you wish to use geoip based flags, your GEOIP_PATH and GIS library must be set up correctly.
