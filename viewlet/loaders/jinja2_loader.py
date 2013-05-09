# coding=utf-8
from django.conf import settings as django_settings
from django.utils.importlib import import_module
from jinja2 import FileSystemLoader, PackageLoader, ChoiceLoader
from jinja2.environment import Environment
from jinja2.filters import do_mark_safe
import viewlet
from viewlet.conf import settings


def call_viewlet(context, name, *args):
    """
    Jinja2 shortcut.
    Put this in globals of the jinja2 enviornment, named 'viewlet':
        JINJA2_GLOBALS = {
            'viewlet': 'viewlet.loaders.jinja2_loader.call_viewlet'
        }
    Then from the template a viewlet can be rendered with:
        {{ viewlet('name-of-viewlet', *args) }}
    """
    return mark_safe(viewlet.call(name, context, *args))
call_viewlet.contextfunction = True


def create_env():
    x = ((FileSystemLoader, django_settings.TEMPLATE_DIRS),
         (PackageLoader, django_settings.INSTALLED_APPS))
    loaders = [loader(p) for loader, places in x for p in places]
    env = Environment(loader=ChoiceLoader(loaders))
    env.globals.update(viewlet=call_viewlet)
    return env


def get_env():
    jinja2_env_module = settings.VIEWLET_JINJA2_ENVIRONMENT
    module, environment = jinja2_env_module.rsplit('.', 1)
    imported_module = import_module(module)
    jinja2_env = getattr(imported_module, environment)
    if callable(jinja2_env):
        jinja2_env = jinja2_env()
    return jinja2_env
env = get_env()


def render_to_string(template_name, context):
    return get_template(template_name).render(context)


def get_template(template_name):
    return env.get_template(template_name)


def mark_safe(value):
    return do_mark_safe(value)
