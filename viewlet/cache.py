# coding=utf-8
from __future__ import unicode_literals
import hashlib
from .conf import settings
from .exceptions import DeprecatedKeyFormat, WrongKeyFormat


def get_cache(alias=None):
    from django.core import cache
    try:
        c = cache.get_cache(alias or settings.VIEWLET_DEFAULT_CACHE_ALIAS)
    except (cache.InvalidCacheBackendError, ValueError):
        c = cache.cache
    if not hasattr(c, 'clear'):  # Django < 1.2
        c.clear = c._cache.clear
    return c


def join_args(args):
    return u':'.join(map(repr, args))


def digest_args(args):
    return hashlib.sha1(join_args(args).encode('utf8')).hexdigest()


def make_key_args_fmt(viewlet, args):
    if viewlet.key:
        if '%' in viewlet.key:
            raise DeprecatedKeyFormat
        if viewlet.has_args and '{args}' not in viewlet.key:
            raise WrongKeyFormat

    fmt = viewlet.key or 'viewlet:%s:{args}' % viewlet.name
    return fmt.format(args=args)


def make_key_args_join(viewlet, args):
    return make_key_args_fmt(viewlet, join_args(args))


def make_key_args_digest(viewlet, args):
    return make_key_args_fmt(viewlet, digest_args(args))
