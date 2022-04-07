from django.http import HttpResponse

import viewlet


def viewlet_view(request, name):
    context = {"request": request}
    kwargs = {"request": request}

    # This feels klunky, is there a better way to do it?
    kwargs.update({k: ",".join(request.GET.getlist(k)) for k in request.GET})

    output = viewlet.call(name, context, **kwargs)
    resp = HttpResponse(output)
    resp["X-Robots-Tag"] = "noindex"
    return resp
