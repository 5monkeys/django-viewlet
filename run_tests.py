#!/usr/bin/env python
# coding=utf-8
import sys
import os

import django
from django.conf import settings

ROOT = os.path.join(os.path.dirname(__file__), 'viewlet/tests')


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
            'viewlet.tests',
        ],
        'MIDDLEWARE_CLASSES': [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        'MEDIA_ROOT': '/tmp/viewlet/media',
        'STATIC_ROOT': '/tmp/viewlet/static',
        'MEDIA_URL': '/media/',
        'STATIC_URL': '/static/',
        'ROOT_URLCONF': 'viewlet.tests.urls',
        'SECRET_KEY': "iufoj=mibkpdz*%bob952x(%49rqgv8gg45k36kjcg76&-y5=!",

        'TEMPLATE_CONTEXT_PROCESSORS': [],
        'TEMPLATE_DIRS': (os.path.join(ROOT, 'template_dir'),),

        'TEMPLATES': [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'DIRS': (os.path.join(ROOT, 'template_dir'),),
                'OPTIONS': {
                    'debug': True,
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ]
                }
            }
        ],

        'JINJA2_ENVIRONMENT_OPTIONS': {
            'optimized': False  # Coffin config
        },
        'JINJA_CONFIG': {
            'autoescape': True  # Jingo config
        }
    }

    if django.VERSION >= (1, 10):
        conf['MIDDLEWARE'] = conf.pop('MIDDLEWARE_CLASSES')

    if django.VERSION < (1, 8):
        conf.pop('TEMPLATES')
    else:
        conf.pop('TEMPLATE_DEBUG')
        conf.pop('TEMPLATE_CONTEXT_PROCESSORS')
        conf.pop('TEMPLATE_DIRS')

    if django.VERSION >= (1, 3):
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
