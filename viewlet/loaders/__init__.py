# coding=utf-8
from __future__ import unicode_literals
import six
from viewlet.conf import settings


def get_loader():
    if settings.VIEWLET_TEMPLATE_ENGINE.lower() == 'jinja2':
        from . import jinja2_loader as loader
    else:
        from . import django_loader as loader
    return loader


def render(*args, **kwargs):
    loader = get_loader()
    return loader.render_to_string(*args, **kwargs)


def mark_safe(value):
    loader = get_loader()
    return loader.mark_safe(value)


def querydict_to_kwargs(querydict):
    def make_key(k):
        if six.PY3:
            return k
        else:
            return k.encode('utf-8')
    return dict((make_key(k), ','.join(querydict.getlist(k))) for k in querydict)
