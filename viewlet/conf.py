from django.conf import settings as django_settings


class ViewletSettings(dict):

    def __init__(self, **conf):
        super(ViewletSettings, self).__init__(conf)

        # Override defualts with django settings
        for key, value in conf.iteritems():
            setattr(self, key, getattr(django_settings, key, value))

    def use_django(self):
        return self.VIEWLET_TEMPLATE_ENGINE == 'django'

    def use_jinja2(self):
        return self.VIEWLET_TEMPLATE_ENGINE == 'jinja2'


settings = ViewletSettings(**{
    'VIEWLET_TEMPLATE_ENGINE': 'django'
})
