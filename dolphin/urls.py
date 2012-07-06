from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'dolphin.views.dolphin_test'),
    url(r'^js/$', 'dolphin.views.js'),
    url(r'^json/$', 'dolphin.views.json'),
)
