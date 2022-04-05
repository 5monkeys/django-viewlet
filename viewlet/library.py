import types

from .const import DEFAULT_TIMEOUT


class Singleton(type):
    """
    Singleton type
    """

    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance


class Library(dict):
    """
    The Library stores references to registered viewlets
    """

    __metaclass__ = Singleton

    def autodiscover(self):
        """
        Autodiscover decorated viewlets.
        Imports all views.py and viewlets.py to trigger the decorators.
        """
        from django.conf import settings

        from .compat import import_module

        for app in settings.INSTALLED_APPS:
            try:
                import_module("%s.views" % app)
            except ImportError:
                pass

            try:
                import_module("%s.viewlets" % app)
            except ImportError:
                pass

    def get(self, name):
        """
        Getter for a registered viewlet.
        If not found then scan for decorated viewlets.
        """
        if name not in self.keys():
            self.autodiscover()

        if name not in self:
            from .exceptions import UnknownViewlet

            raise UnknownViewlet('Unknown viewlet "%s"' % name)

        return self[name]

    def add(self, viewlet):
        """
        Adds a registered viewlet to the Library dict
        """
        if viewlet.name not in self.keys():
            self[viewlet.name] = viewlet

    def _decorator(
        self,
        name=None,
        template=None,
        key=None,
        timeout=DEFAULT_TIMEOUT,
        using=None,
        cached=True,
    ):
        """
        Handles both decorator pointer and caller (with or without arguments).
        Creates a Viewlet instance to wrap the decorated function with.
        """
        from .models import Viewlet

        if isinstance(name, types.FunctionType):

            def declare(func):
                viewlet = Viewlet(self)
                return viewlet.register(func)

            return declare(name)
        else:
            viewlet = Viewlet(
                self,
                name=name,
                template=template,
                key=key,
                timeout=timeout,
                using=using,
                cached=cached,
            )
            return viewlet.register


library = Library()
