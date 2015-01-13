from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import ArgyverView, DownloadView

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = patterns('', url(r'^__debug__/', include(debug_toolbar.urls)))
else:
    urlpatterns = patterns('')

urlpatterns += patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^download/(?P<path>.*)/(?P<version>\d{8}-\d{6})?$', DownloadView.as_view(), name='download'),
    url(r'^(?P<path>.*)/?$', ArgyverView.as_view()),
)
