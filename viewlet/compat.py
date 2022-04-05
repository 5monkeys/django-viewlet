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

        return patterns("", *urls)

    return list(urls)


if django.VERSION < (1, 4):
    from django.conf.urls.defaults import include, url
else:
    from django.conf.urls import include, url


if django.VERSION < (1, 8):
    from django.template import Context
else:

    def Context(context):
        return context


if PY3:
    from django.utils.encoding import smart_bytes, smart_text
else:
    from django.utils.encoding import (
        smart_str as smart_bytes,
        smart_unicode as smart_text,
    )


def get_func_args(func):
    if PY3:
        return list(inspect.signature(func).parameters.keys())
    return inspect.getargspec(func).args


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
    "smart_text",
    "smart_bytes",
    "get_func_args",
    "import_module",
    "url",
    "patterns",
    "include",
    "Context",
]
