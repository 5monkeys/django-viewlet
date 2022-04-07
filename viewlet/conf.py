from django.conf import settings as django_settings


class ViewletSettings(dict):
    def __init__(self, **conf):
        super().__init__(conf)

        # Override defaults with django settings
        for key in conf:
            setattr(self, key, getattr(django_settings, key, conf[key]))

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


settings = ViewletSettings(
    **{
        "VIEWLET_DEFAULT_CACHE_ALIAS": "viewlet",
        "VIEWLET_CACHE_KEY_FUNCTION": "viewlet.cache.make_key_args_digest",
        "VIEWLET_CACHE_KEY_MAX_LENGTH": 255,
        "VIEWLET_INFINITE_CACHE_TIMEOUT": 31104000,  # 60*60*24*30*12, about a year
        "VIEWLET_JINJA2_ENVIRONMENT": "viewlet.loaders.jinja2_loader.create_env",
    }
)
