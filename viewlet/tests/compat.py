import django

if django.VERSION < (1, 8):
    from django.template.loader import get_template_from_string
else:
    from django.template import engines

    def get_template_from_string(template_code):
        return engines['django'].from_string(template_code)


if django.VERSION < (2, 0):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


__all__ = [
    'get_template_from_string', 'reverse',
]
