import logging
import re
from django import template
from django.template import TemplateSyntaxError
import viewlet
from viewlet.exceptions import UnknownViewlet
from viewlet.loaders import mark_safe

logger = logging.getLogger(__name__)
register = template.Library()
kwarg_re = re.compile(r'(?:(\w+)=)?(.+)')


class ViewletNode(template.Node):

    def __init__(self, viewlet_name, args, kwargs):
        self.viewlet_name = viewlet_name
        self.viewlet_args = args
        self.viewlet_kwargs = kwargs

    def render(self, context):
        try:
            args = [arg.resolve(context) for arg in self.viewlet_args]
            kwargs = dict((key, value.resolve(context)) for key, value in self.viewlet_kwargs.items())
            template = viewlet.call(self.viewlet_name, context, *args, **kwargs)
            return mark_safe(template)
        except UnknownViewlet as e:
            logger.exception(e)
            raise


@register.tag(name='viewlet')
def viewlet_tag(parser, token):
    bits = token.split_contents()[1:]
    viewlet_name = bits.pop(0)
    args = []
    kwargs = {}

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError('Malformed arguments to viewlet tag')
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return ViewletNode(viewlet_name, args, kwargs)
