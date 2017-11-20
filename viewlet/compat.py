import sys
import django

PY3 = sys.version_info[0] == 3


def patterns(*urls):
    if django.VERSION < (1, 10):
        if django.VERSION < (1, 6):
            from django.conf.urls.defaults import patterns
        else:
            from django.conf.urls import patterns

        return patterns('', *urls)

    return list(urls)


if django.VERSION < (1, 6):
    from django.conf.urls.defaults import url
else:
    from django.conf.urls import url


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


__all__ = [
    'smart_text',
    'smart_bytes',
    'url',
    'patterns',
    'Context'
]
