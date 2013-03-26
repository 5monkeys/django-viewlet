# coding=utf-8
from viewlet.library import library
from viewlet.exceptions import ViewletException
try:
    from jinja2.filters import do_mark_safe
    from coffin.template.loader import render_to_string  # nopep8
except ImportError:
    raise ViewletException('You need coffin along with jinja2 for django-viewlet to work')


def mark_safe(output):
    return do_mark_safe(output)


def call_viewlet(context, name, *args):
    """
    Jinja2 shortcut.
    Put this in globals of the jinja2 enviornment, named 'viewlet'.
    Then from the template a viewlet can be rendered with:
    {{ viewlet('name-of-viewlet', *args) }}
    """
    return library.get(name).call(context, *args)
call_viewlet.contextfunction = True
