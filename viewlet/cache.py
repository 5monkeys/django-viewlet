# coding=utf-8
from .conf import settings


def get_cache(alias=settings.VIEWLET_DEFAULT_CACHE_ALIAS):
    from django.core import cache
    try:
        return cache.get_cache(alias)
    except (cache.InvalidCacheBackendError, ValueError):
        return cache.cache
