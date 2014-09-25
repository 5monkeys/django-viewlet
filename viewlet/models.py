# coding=utf-8
from __future__ import unicode_literals
import six
import warnings
from inspect import getargspec
from django.template.context import BaseContext
try:
    from django.utils.encoding import smart_text, smart_bytes
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text, smart_str as smart_bytes

from viewlet.cache import get_cache
from viewlet.conf import settings
from viewlet.loaders import render

cache = get_cache()
DEFAULT_CACHE_TIMEOUT = cache.default_timeout


class Viewlet(object):
    """
    Representation of a viewlet
    """

    def __init__(self, library, name=None, template=None, key=None, timeout=DEFAULT_CACHE_TIMEOUT, cached=True):
        self.library = library
        self.name = name
        self.template = template
        self.key = key
        self.key_mod = False
        if timeout is None:
            # Handle infinite caching, due to Django's cache backend not respecting 0
            self.timeout = settings.VIEWLET_INFINITE_CACHE_TIMEOUT
        else:
            self.timeout = timeout
        if not cached:
            self.timeout = 0
            warnings.warn('Keyword argument "cache" is deprecated, use timeout=0 to disable cache',
                          DeprecationWarning)

    def register(self, func):
        """
        Initial decorator wrapper that configures the viewlet instance,
        adds it to the library and then returns a pointer to the call
        function as the actual wrapper
        """
        self.viewlet_func = func
        self.viewlet_func_args = getargspec(func).args

        if not self.name:
            self.name = getattr(func, 'func_name', getattr(func, '__name__'))

        func_argcount = len(self.viewlet_func_args) - 1
        if self.timeout:
            # TODO: HASH KEY
            self.key = u'viewlet:%s(%s)' % (self.name, ','.join(['%s' for _ in range(0, func_argcount)]))
            self.key_mod = func_argcount > 0
        self.library.add(self)

        return self.call

    def _build_args(self, *args, **kwargs):
        viewlet_func_kwargs = dict((self.viewlet_func_args[i], args[i]) for i in range(0, len(args)))
        viewlet_func_kwargs.update(dict((k, kwargs[k]) for k in kwargs if k in self.viewlet_func_args))
        return [viewlet_func_kwargs.get(arg) for arg in self.viewlet_func_args]

    def _build_cache_key(self, *args):
        """
        Build cache key based on viewlet argument except initial context argument.
        """
        return self.key if not self.key_mod else self.key % tuple(args)

    def _cache_get(self, key):
        return cache.get(key)

    def _cache_set(self, key, value):
        timeout = self.timeout

        # Avoid pickling string like objects
        if isinstance(value, six.string_types):
            value = smart_bytes(value)
        cache.set(key, value, timeout)

    def call(self, *args, **kwargs):
        """
        The actual wrapper around the decorated viewlet function.
        """
        refresh = kwargs.pop('refresh', False)
        merged_args = self._build_args(*args, **kwargs)
        output = self._call(merged_args, refresh)

        # Render template for context viewlets
        if self.template:
            context = merged_args[0]
            if isinstance(context, BaseContext):
                context.push()
            else:
                context = dict(context)
            context.update(output)

            output = self.render(context)

            if isinstance(context, BaseContext):
                context.pop()

        return smart_text(output)

    def _call(self, merged_args, refresh=False):
        """
        Executes the actual call to the viewlet function and handles all the cache logic
        """

        cache_key = self._build_cache_key(*merged_args[1:])

        if refresh or not self.is_using_cache():
            output = None
        else:
            output = self._cache_get(cache_key)

        # First viewlet execution, forced refresh or cache timeout
        if output is None:
            output = self.viewlet_func(*merged_args)
            if self.is_using_cache():
                self._cache_set(cache_key, output)

        return output

    def is_using_cache(self):
        return self.timeout != 0

    def render(self, context):
        """
        Renders the viewlet template.
        The render import is based on settings.VIEWLET_TEMPLATE_ENGINE (default django).
        """
        return render(self.template, context)

    def refresh(self, *args):
        """
        Shortcut to _call() with the refresh arg set to True to force a cache update.
        """
        merged_args = self._build_args({}, *args)
        return self._call(merged_args, refresh=True)

    def expire(self, *args):
        """
        Clears cached viewlet based on args
        """
        merged_args = self._build_args({}, *args)
        dyna_key = self._build_cache_key(*merged_args[1:])
        cache.delete(dyna_key)
