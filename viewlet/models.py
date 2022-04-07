import inspect
import warnings
from importlib import import_module

from django.template.context import BaseContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes, smart_str

from .cache import get_cache
from .conf import settings
from .const import DEFAULT_TIMEOUT


def import_by_path(path):
    m, _, f = path.rpartition(".")
    return getattr(import_module(m), f)


default_key_func = import_by_path(settings.VIEWLET_CACHE_KEY_FUNCTION)


class Viewlet:
    """
    Representation of a viewlet
    """

    def __init__(
        self,
        library,
        name=None,
        template=None,
        key=None,
        timeout=DEFAULT_TIMEOUT,
        using=None,
        cached=True,
    ):
        self.library = library
        self.name = name
        self.template = template
        self.key = key
        self.has_args = False
        self.cache_alias = using
        self.cache = get_cache(alias=using)
        if timeout is None:
            # Handle infinite caching, due to Django's cache backend not respecting 0
            self.timeout = settings.VIEWLET_INFINITE_CACHE_TIMEOUT
        elif timeout is DEFAULT_TIMEOUT:
            self.timeout = self.cache.default_timeout
        else:
            self.timeout = timeout
        if not cached:
            self.timeout = 0
            warnings.warn(
                'Keyword argument "cached" is deprecated, use timeout=0 to disable cache',
                DeprecationWarning,
            )

    def register(self, func):
        """
        Initial decorator wrapper that configures the viewlet instance,
        adds it to the library and then returns a pointer to the call
        function as the actual wrapper
        """
        self.viewlet_func = func
        self.viewlet_func_args = list(inspect.signature(func).parameters.keys())
        self.has_args = len(self.viewlet_func_args) > 1

        if not self.name:
            self.name = getattr(func, "func_name", func.__name__)

        self.library.add(self)

        def call_with_refresh(*args, **kwargs):
            return self.call(*args, **kwargs)

        call_with_refresh.refresh = self.refresh
        call_with_refresh.expire = self.expire

        return call_with_refresh

    def _build_args(self, *args, **kwargs):
        viewlet_func_kwargs = {
            self.viewlet_func_args[i]: args[i] for i in range(0, len(args))
        }
        viewlet_func_kwargs.update(
            {k: kwargs[k] for k in kwargs if k in self.viewlet_func_args}
        )
        return [viewlet_func_kwargs.get(arg) for arg in self.viewlet_func_args]

    def _build_cache_key(self, *args):
        """
        Build cache key based on viewlet argument except initial context argument.
        """
        key = self.key
        if key and callable(key):
            key = key(self, args)
        else:
            key = default_key_func(self, args)
        max_len = settings.VIEWLET_CACHE_KEY_MAX_LENGTH
        assert (
            len(key) <= max_len
        ), "Viewlet cache key is too long: len(`{key}`) > {max_len}".format(
            key=key, max_len=max_len
        )
        return key

    def _cache_get(self, key):
        s = self.cache.get(key)
        if isinstance(s, bytes):
            s = smart_str(s)
        return s

    def _cache_set(self, key, value):
        timeout = self.timeout

        # Avoid pickling string like objects
        if isinstance(value, str):
            value = smart_bytes(value)
        self.cache.set(key, value, timeout)

    def call(self, *args, **kwargs):
        """
        The actual wrapper around the decorated viewlet function.
        """
        refresh = kwargs.pop("refresh", False)
        request = kwargs.pop("request", None)
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
            kw = {"request": request}
            output = self.render(context, **kw)

            if isinstance(context, BaseContext):
                context.pop()

        return smart_str(output)

    def _call(self, merged_args, refresh=False):
        """
        Executes the actual call to the viewlet function and handles all the cache logic
        """

        if self.is_using_cache():
            cache_key = self._build_cache_key(*merged_args[1:])
        else:
            cache_key = None

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

    def render(self, context, **kwargs):
        """
        Renders the viewlet template.
        """
        return render_to_string(self.template, context, **kwargs)

    def refresh(self, *args, **kwargs):
        """
        Shortcut to _call() with the refresh arg set to True to force a cache update.
        """
        merged_args = self._build_args({}, *args, **kwargs)
        return self._call(merged_args, refresh=True)

    def expire(self, *args, **kwargs):
        """
        Clears cached viewlet based on args
        """
        merged_args = self._build_args({}, *args, **kwargs)
        dyna_key = self._build_cache_key(*merged_args[1:])
        self.cache.delete(dyna_key)
