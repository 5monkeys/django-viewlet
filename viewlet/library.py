import types
from django.utils.importlib import import_module
from viewlet.exceptions import ViewletException


class Singleton(type):
    """
    Singleton type
    """

    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
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
        for app in settings.INSTALLED_APPS:
            try:
                import_module('%s.views' % app)
                import_module('%s.viewlets' % app)
            except ImportError:
                continue

    def get(self, name):
        """
        Getter for a registered viewlet.
        If not found then scan for decorated viewlets.
        """
        if not name in self.keys():
            self.autodiscover()

        try:
            return self[name]
        except KeyError:
            raise ViewletException(u'Unknown viewlet "%s"' % name)

    def add(self, viewlet):
        """
        Adds a registered viewlet to the Library dict
        """
        if not viewlet.name in self.keys():
            self[viewlet.name] = viewlet

    def _decorator(self, name=None, template=None, key=None, timeout=60, cached=True):
        """
        Handles both decorator pointer and caller (with or without arguments).
        Creates a Viewlet instance to wrap the decorated function with.
        """
        from viewlet.model import Viewlet

        if isinstance(name, types.FunctionType):
            def declare(func):
                viewlet = Viewlet(self)
                return viewlet.register(func)
            return declare(name)
        else:
            viewlet = Viewlet(self, name, template, key, timeout, cached)
            return viewlet.register


library = Library()
