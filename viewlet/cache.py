from django.core.cache import InvalidCacheBackendError


def get_cache():
    try:
        from django.core.cache import get_cache
        cache = get_cache('viewlet')
    except InvalidCacheBackendError:
        from django.core.cache import cache
    return cache
