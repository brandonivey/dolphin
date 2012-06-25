from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from ajax_select import urls as ajax_select_urls


# Uncomment the next two lines to enable the admin:
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testapp.views.home', name='home'),
    # url(r'^testapp/', include('testapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', 'testapp.views.home'),
    url(r'^flag_is_active/(?P<slug>[\w-]+)/$', 'testapp.views.is_active'),
    url(r'^dolphin/js/$', 'dolphin.views.js'),
    url(r'^dolphin/json/$', 'dolphin.views.json'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/lookups/', include(ajax_select_urls)),
)
