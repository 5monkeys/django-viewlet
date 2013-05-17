#!/usr/bin/env python
# coding=utf-8
import sys
import django
from django.conf import settings


def main():
    conf = {'DEBUG': True,
            'TEMPLATE_DEBUG': True,
            'INSTALLED_APPS': ['viewlet', 'viewlet.tests'],
            'MEDIA_ROOT': '/tmp/viewlet/media',
            'STATIC_ROOT': '/tmp/viewlet/static',
            'MEDIA_URL': '/media/',
            'STATIC_URL': '/static/',
            'ROOT_URLCONF': 'viewlet.tests.urls',
            'SECRET_KEY': "iufoj=mibkpdz*%bob952x(%49rqgv8gg45k36kjcg76&-y5=!",
            'JINJA2_ENVIRONMENT_OPTIONS': {
                'optimized': False  # Coffin config
            },
            'JINJA_CONFIG': {
                'autoescape': True  # Jingo config
            }
    }

    if django.VERSION[:2] >= (1, 3):
        conf.update(DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        })

        conf.update(CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            }
        })
    else:
        conf.update(DATABASE_ENGINE='sqlite3')
        conf.update(CACHE_BACKEND='locmem://')

    settings.configure(**conf)

    from django.test.utils import get_runner
    test_runner = get_runner(settings)(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['viewlet'])

    sys.exit(failures)


if __name__ == '__main__':
    main()
