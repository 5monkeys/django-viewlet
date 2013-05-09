from inspect import getargspec
from django.template.context import BaseContext
from django.utils.encoding import smart_str
from viewlet.cache import get_cache
from viewlet.exceptions import ViewletException
from viewlet.loaders import render, mark_safe

cache = get_cache()
MAX_CACHE_TIMEOUT = 2591999


class Viewlet(object):
    """
    Representation of a viewlet
    """

    def __init__(self, library, name=None, template=None, key=None, timeout=60, cached=True):
        self.library = library
        self.name = name
        self.template = template
        self.key = key
        self.key_mod = False
        if not cached:
            self.timeout = None
        elif timeout:
            self.timeout = timeout
        else:
            self.timeout = MAX_CACHE_TIMEOUT

    def register(self, func):
        """
        Initial decorator wrapper that configures the viewlet instance,
        adds it to the library and then returns a pointer to the call
        function as the actual wrapper
        """
        self.viewlet_func = func
        self.viewlet_func_args = getargspec(func).args

        if not self.name:
            self.name = func.func_name

        func_argcount = len(self.viewlet_func_args) - 1
        if self.key:
            cache_key_argcount = self.key.count('%s')
            if cache_key_argcount == func_argcount:
                self.key_mod = True
            else:
                raise ViewletException(u'Invalid viewlet cache key for "%s": found %s, expected %s' % (self.name,
                                                                                                       cache_key_argcount,
                                                                                                       func_argcount))
        elif self.timeout is not None:
            self.key = u'viewlet:%s(%s)' % (self.name, ','.join(['%s' for _ in range(0, func_argcount)]))
            self.key_mod = func_argcount > 0
        self.library.add(self)

        return self.call

    def _build_args(self, *args, **kwargs):
        viewlet_func_kwargs = dict((self.viewlet_func_args[i], args[i]) for i in range(0, len(args)))
        viewlet_func_kwargs.update(dict((k, v) for k, v in kwargs.iteritems() if k in self.viewlet_func_args))
        return [viewlet_func_kwargs.get(arg) for arg in self.viewlet_func_args]

    def _build_cache_key(self, *args):
        return self.key if not self.key_mod else self.key % tuple(args[1:])

    def call(self, *args, **kwargs):
        """
        The actual wrapper around the decorated viewlet function.
        """
        refresh = kwargs.get('refresh', False)

        merged_args = self._build_args(*args, **kwargs)
        dyna_key = self._build_cache_key(*merged_args)
        if refresh or not self.use_cache():
            output = None
        else:
            output = cache.get(dyna_key)

        if output is None:
            output = self.viewlet_func(*merged_args)

            if self.template:
                context = merged_args[0]

                if isinstance(context, BaseContext):
                    context.push()
                else:
                    context = dict(context)

                context.update(output)
                output = self.render(context)
                self._save(dyna_key, context)
                if isinstance(context, BaseContext):
                    context.pop()
            else:
                output = smart_str(output)
                self._save(dyna_key, output)
        elif self.template:
            output = self.render(output)

        return mark_safe(output)

    def use_cache(self):
        return self.key and self.timeout is not None

    def _save(self, key, content):
        if self.use_cache():
            cache.set(key, content, self.timeout)

    def render(self, context):
        """
        Renders the viewlet template.
        The render import is based on settings.VIEWLET_TEMPLATE_ENGINE (default django).
        """
        return render(self.template, context)

    def refresh(self, *args):
        """
        Shortcut to call() with the refresh arg set to True to force a cache update.
        """
        return self.call({}, *args, refresh=True)

    def expire(self, *args):
        """
        Clears cached viewlet based on args
        """
        merged_args = self._build_args({}, *args)
        dyna_key = self._build_cache_key(*merged_args)
        cache.delete(dyna_key)
