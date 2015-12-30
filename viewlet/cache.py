# coding=utf-8
from __future__ import unicode_literals
from .conf import settings


def get_cache(alias=None):
    import django
    from django.core import cache
    try:
        key = alias or settings.VIEWLET_DEFAULT_CACHE_ALIAS
        if django.VERSION > (1, 8):
            c = cache.caches[key]
        else:
            c = cache.get_cache(key)
    except (cache.InvalidCacheBackendError, ValueError):
        c = cache.cache
    if not hasattr(c, 'clear'):  # Django < 1.2
        c.clear = c._cache.clear
    return c
