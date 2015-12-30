# coding=utf-8
from __future__ import unicode_literals
from django.conf import settings as django_settings
from importlib import import_module
from jinja2 import FileSystemLoader, PackageLoader, ChoiceLoader, nodes
from jinja2.environment import Environment
from jinja2.ext import Extension
from jinja2.filters import do_mark_safe
import viewlet
from viewlet.conf import settings


class ViewletExtension(Extension):
    tags = set(['viewlet'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        viewlet_args = []
        name = None
        first = True
        while parser.stream.current.type != 'block_end':
            if not first:
                parser.stream.expect('comma')
                viewlet_args.append(parser.parse_expression())
            else:
                name = parser.parse_expression()
            first = False
        context = nodes.ContextReference()
        return nodes.CallBlock(
            self.call_method('_call_viewlet', args=[name, context, nodes.List(viewlet_args)]),
            [], [], []).set_lineno(lineno)

    def _call_viewlet(self, name, context, viewlet_args, caller=None):
        context = context.get_all()
        return mark_safe(viewlet.call(name, context, *viewlet_args))


def create_env():
    x = ((FileSystemLoader, django_settings.TEMPLATE_DIRS),
         (PackageLoader, django_settings.INSTALLED_APPS))
    loaders = [loader(p) for loader, places in x for p in places]
    env = Environment(loader=ChoiceLoader(loaders), extensions=[ViewletExtension])
    return env


_env = None


def get_env():
    global _env
    if _env:
        return _env

    jinja2_env_module = settings.VIEWLET_JINJA2_ENVIRONMENT
    module, environment = jinja2_env_module.rsplit('.', 1)
    imported_module = import_module(module)
    jinja2_env = getattr(imported_module, environment)
    if callable(jinja2_env):
        jinja2_env = jinja2_env()
    _env = jinja2_env
    return jinja2_env


def render_to_string(template_name, context):
    return get_template(template_name).render(context)


def get_template(template_name):
    return get_env().get_template(template_name)


def mark_safe(value):
    return do_mark_safe(value)
