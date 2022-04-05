import django
from django.http import HttpResponse
from django.template.context import RequestContext

import viewlet
from viewlet.loaders import querydict_to_kwargs


def viewlet_view(request, name):
    if django.VERSION >= (1, 8):
        context = {"request": request}
        kwargs = {"request": request}
    else:
        context = RequestContext(request)
        kwargs = {}

    kwargs.update(querydict_to_kwargs(request.GET))
    output = viewlet.call(name, context, **kwargs)
    resp = HttpResponse(output)
    resp["X-Robots-Tag"] = "noindex"
    return resp
