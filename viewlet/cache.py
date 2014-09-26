# coding=utf-8
from __future__ import unicode_literals
from .conf import settings


def get_cache(alias=None):
    from django.core import cache
    try:
        c = cache.get_cache(alias or settings.VIEWLET_DEFAULT_CACHE_ALIAS)
    except (cache.InvalidCacheBackendError, ValueError):
        c = cache.cache
    if not hasattr(c, 'clear'):  # Django < 1.2
        c.clear = c._cache.clear
    return c
