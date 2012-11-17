from viewlet.conf import settings
if settings.use_jinja2():
    from viewlet.utils import jinja2_loader as loader
else:
    from viewlet.utils import django_loader as loader


render = loader.render_to_string
mark_safe = loader.mark_safe


def get_context_object(model, pk, context):
    return context.get(model.__name__.lower(), model.objects.get(pk=pk))


def querydict_to_kwargs(querydict):
    return dict((k.encode('utf-8'), ','.join(v)) for k, v in querydict.iteritems())
