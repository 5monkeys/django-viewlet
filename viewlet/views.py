# coding=utf-8
from __future__ import unicode_literals
from django.http import HttpResponse
from django.template.context import RequestContext
import viewlet
from viewlet.loaders import querydict_to_kwargs


def viewlet_view(request, name):
    context = RequestContext(request)
    kwargs = querydict_to_kwargs(request.GET)
    output = viewlet.call(name, context, **kwargs)
    return HttpResponse(output)
