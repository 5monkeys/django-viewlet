import inspect
import sys
import django

PY3 = sys.version_info[0] == 3


def patterns(*urls):
    if django.VERSION < (1, 8):
        if django.VERSION < (1, 4):
            from django.conf.urls.defaults import patterns
        else:
            from django.conf.urls import patterns

        return patterns('', *urls)

    return list(urls)


if django.VERSION < (1, 4):
    from django.conf.urls.defaults import url, include
else:
    from django.conf.urls import url, include


if django.VERSION < (1, 8):
    from django.template import Context
else:
    def Context(context):
        return context


if PY3:
    from django.utils.encoding import smart_text, smart_bytes
else:
    from django.utils.encoding import (
        smart_unicode as smart_text,
        smart_str as smart_bytes
    )


def get_func_args(func):
    if PY3:
        return list(inspect.signature(func).parameters.keys())
    return inspect.getargspec(func).args


def get_func_defaults(func):
    if PY3:
        params = inspect.signature(func).parameters
        return dict((k, v.default) for k, v in params.items() if not v.empty)
    spec = inspect.getargspec(func)
    vals = spec.defaults
    if not vals:
        return {}
    keys = spec.args[-len(vals):]
    return dict(zip(keys, vals))


def import_module(name):
    if sys.version_info < (2, 7):
        if django.VERSION < (1, 7):
            from django.utils.importlib import import_module
            return import_module(name)
        __import__(name)
        return sys.modules[name]
    from importlib import import_module
    return import_module(name)


__all__ = [
    'smart_text',
    'smart_bytes',
    'get_func_args',
    'import_module',
    'url',
    'patterns',
    'include',
    'Context'
]
