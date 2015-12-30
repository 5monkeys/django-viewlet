#!/usr/bin/env python
# coding=utf-8
import sys

import django
from django.conf import settings


def main():
    conf = {
        'DEBUG': True,
        'TEMPLATE_DEBUG': True,
        'INSTALLED_APPS': [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django.contrib.flatpages',
            'viewlet',
            'viewlet.tests'
        ],
        'MIDDLEWARE_CLASSES': [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        ],
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

    if django.VERSION >= (1, 7):
        django.setup()

    from django.test.utils import get_runner
    if django.VERSION < (1, 2):
        failures = get_runner(settings)(['viewlet'], verbosity=2, interactive=True)
    else:
        test_runner = get_runner(settings)(verbosity=2, interactive=True)
        failures = test_runner.run_tests(['viewlet'])

    sys.exit(failures)


if __name__ == '__main__':
    main()
