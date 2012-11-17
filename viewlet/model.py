from inspect import getargspec
from viewlet.exceptions import ViewletException
from viewlet.utils import render, mark_safe
#try:
from django.core.cache import cache
from django.template.context import RequestContext, Context
#except ImportError:
#    e.g. installing package, etc.
#    pass


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
        self.timeout = timeout if cached else 0

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
        elif self.timeout != 0:
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

        output = None if refresh or not self.key else cache.get(dyna_key)

        if output is None:
            output = self.viewlet_func(*merged_args)

            if self.template:
                context = merged_args[0]

                if isinstance(context, RequestContext) or isinstance(context, Context):
                    context.push()
                else:
                    context = dict(context)

                context.update(output)
                output = self.render(context)

                if isinstance(context, RequestContext) or isinstance(context, Context):
                    context.pop()

            if self.key:
                cache.set(dyna_key, output, self.timeout)

        return mark_safe(output)

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
