# coding=utf-8
from .conf import settings


def get_cache(alias=None):
    from django.core import cache
    try:
        return cache.get_cache(alias or settings.VIEWLET_DEFAULT_CACHE_ALIAS)
    except (cache.InvalidCacheBackendError, ValueError):
        return cache.cache
