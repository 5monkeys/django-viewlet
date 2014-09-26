# coding=utf-8
from django.template import TemplateSyntaxError


class ViewletException(Exception):
    pass


class UnknownViewlet(TemplateSyntaxError):
    pass
