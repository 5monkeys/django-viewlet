import hashlib

from django.utils.encoding import smart_str

from .conf import settings
from .exceptions import DeprecatedKeyFormat, WrongKeyFormat


def get_cache(alias=None):
    from django.core import cache

    try:
        key = alias or settings.VIEWLET_DEFAULT_CACHE_ALIAS
        c = cache.caches[key]
    except (cache.InvalidCacheBackendError, ValueError):
        c = cache.cache

    return c


def join_args(args):
    return ":".join(map(smart_str, args))


def digest_args(args):
    return hashlib.sha1(join_args(args).encode("utf8")).hexdigest()


def make_key_args_fmt(viewlet, args):
    if viewlet.key:
        if "%" in viewlet.key:
            raise DeprecatedKeyFormat
        if viewlet.has_args and "{args}" not in viewlet.key:
            raise WrongKeyFormat

    fmt = viewlet.key or "viewlet:%s:{args}" % viewlet.name
    return fmt.format(args=args)


def make_key_args_join(viewlet, args):
    return make_key_args_fmt(viewlet, join_args(args))


def make_key_args_digest(viewlet, args):
    return make_key_args_fmt(viewlet, digest_args(args))
