# coding=utf-8
import django

DEBUG = TEMPLATE_DEBUG = True

if django.VERSION[:2] >= (1, 3):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }
else:
    DATABASE_ENGINE = 'sqlite3'
    CACHE_BACKEND = 'locmem://'

INSTALLED_APPS = [
    'viewlet',
    'viewlet.tests',
]

MEDIA_ROOT = '/tmp/viewlet/media'
STATIC_ROOT = '/tmp/viewlet/static'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

SECRET_KEY = "iufoj=mibkpdz*%bob952x(%49rqgv8gg45k36kjcg76&-y5=!"
