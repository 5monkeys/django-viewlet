# coding=utf-8
from __future__ import unicode_literals
import django
from ..compat import patterns

if django.VERSION < (1, 6):
    from django.conf.urls.defaults import url, include
else:
    from django.conf.urls import url, include


urlpatterns = patterns(
    url(r'viewlet/', include('viewlet.urls'))
)
