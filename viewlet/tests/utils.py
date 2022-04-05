from django.core.cache.backends.locmem import LocMemCache


class ShortLocMemCache(LocMemCache):
    def __init__(self, name, params):
        LocMemCache.__init__(self, name, params)
        self.default_timeout = float(params.get("TIMEOUT", 0.25))
