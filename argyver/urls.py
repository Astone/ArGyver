from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import ArgyverView

urlpatterns = patterns(
    '',
    url(r'^(?P<path>.*)/?$', ArgyverView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
)
