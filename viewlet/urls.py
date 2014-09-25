# coding=utf-8
from __future__ import unicode_literals
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('viewlet.views', url(r'^(?P<name>.+)/$', 'viewlet_view', name='viewlet'))
