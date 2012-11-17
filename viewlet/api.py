from viewlet.library import library


__all__ = ['viewlet', 'get', 'call', 'refresh']


# The decorator
viewlet = library._decorator


def get(viewlet_name):
    return library.get(viewlet_name)


def call(viewlet_name, context, *args, **kwargs):
    return get(viewlet_name).call(context or {}, *args, **kwargs)


def refresh(name, *args, **kwargs):
    return get(name).refresh(*args, **kwargs)
