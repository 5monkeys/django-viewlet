# coding=utf-8
from __future__ import unicode_literals
from .compat import url, patterns
from . import views


urlpatterns = patterns(
    url(r'^(?P<name>.+)/$', views.viewlet_view, name='viewlet')
)
