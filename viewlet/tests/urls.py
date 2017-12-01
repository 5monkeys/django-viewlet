# coding=utf-8
from __future__ import unicode_literals
from ..compat import patterns, url, include

urlpatterns = patterns(
    url(r'viewlet/', include('viewlet.urls'))
)
