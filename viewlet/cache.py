# coding=utf-8
from .conf import settings


def get_cache(backend=settings.VIEWLET_CACHE_BACKEND):
    from django.core import cache
    try:
        return cache.get_cache(backend)
    except (cache.InvalidCacheBackendError, ValueError):
        return cache.cache
