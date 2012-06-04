from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import ListView

from ajax_select import urls as ajax_select_urls

from dolphin.models import FeatureFlag


# Uncomment the next two lines to enable the admin:
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testapp.views.home', name='home'),
    # url(r'^testapp/', include('testapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', ListView.as_view(queryset=FeatureFlag.objects.all(), template_name="home.html")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/lookups/', include(ajax_select_urls)),
)
