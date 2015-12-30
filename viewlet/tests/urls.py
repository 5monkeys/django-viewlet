# coding=utf-8
from __future__ import unicode_literals
import django

if django.VERSION[:2] < (1, 7):
    try:
        from django.conf.urls import patterns, include
    except ImportError:
        from django.conf.urls.defaults import patterns, include

    urlpatterns = patterns(
        '',
        (r'^viewlet/', include('viewlet.urls')),
    )
else:
    from django.conf.urls import url, include

    urlpatterns = [
        url(r'viewlet/', include('viewlet.urls'))
    ]
