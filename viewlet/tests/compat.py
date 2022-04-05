import functools
import sys

import django

if django.VERSION < (1, 8):
    from django.template.loader import get_template_from_string
else:
    from django.template import engines

    def get_template_from_string(template_code):
        return engines["django"].from_string(template_code)


if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

if django.VERSION < (1, 4):
    override_settings = None
elif django.VERSION < (1, 7):
    from django.test.utils import override_settings
else:
    from django.test import override_settings


if sys.version_info < (2, 7):

    def skipIf(condition, reason):
        def _decorator(test_item):
            @functools.wraps(test_item)
            def _wrapper(*args, **kwargs):
                if condition:
                    sys.stdout.write("skipped %r" % reason)
                else:
                    return test_item(*args, **kwargs)

            return _wrapper

        return _decorator

else:
    from unittest import skipIf


__all__ = [
    "get_template_from_string",
    "reverse",
    "skipIf",
    "override_settings",
]
