# coding=utf-8
from __future__ import unicode_literals
from .compat import urlpatterns
from viewlet import views

try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url


urlpatterns = urlpatterns(
    url(r'^(?P<name>.+)/$', views.viewlet_view, name='viewlet')
)
