Setup
=====

1. Install geoposition if necessary (pip install django-geoposition)
2. Add "dolphin.middleware.LocalStoreMiddleware" to your MIDDLEWARE_CLASSES. If you are
   planning on using Dolphin in middleware, it's suggested you put it before the middleware
   you use it in.
   This allows per-request random testing and per-request caching.
3. Add "dolphin" and "geoposition" to INSTALLED_APPS
4. Ensure that REMOTE_ADDR is pointing to the correct IP address. If not,
   you will have to otherwise patch dolphin.utils.get_ip to use geoip.
5. Load database table using manage.py, either via syncdb or migrate dolphin if using south.
6. If you wish to use geoip based flags, your GEOIP_PATH and GIS library must be set up correctly.
7. If you wish to use the javascript options, add dolphin.views.js and dolphin.views.json to your urls.py.
8. If you wish to use the dolphin test page, add dolphin.views.dolphin_test to your views and enable the
   flag either from your settings.DOLPHIN_TEST_FLAG or "dolphin_test".
