#!/usr/bin/env python
import os
import sys
import warnings

import django
from django.conf import settings

# We do it first before Django loads, and then again in tests
warnings.simplefilter("error")
warnings.filterwarnings("ignore", module="cgi")


ROOT = os.path.join(os.path.dirname(__file__), "viewlet/tests")


def main():
    conf = {
        "DEBUG": True,
        "TEMPLATE_DEBUG": True,
        "INSTALLED_APPS": [
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.flatpages",
            "viewlet",
            "viewlet.tests",
        ],
        "MIDDLEWARE_CLASSES": [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        "MEDIA_ROOT": "/tmp/viewlet/media",
        "STATIC_ROOT": "/tmp/viewlet/static",
        "MEDIA_URL": "/media/",
        "STATIC_URL": "/static/",
        "ROOT_URLCONF": "viewlet.tests.urls",
        "SECRET_KEY": "iufoj=mibkpdz*%bob952x(%49rqgv8gg45k36kjcg76&-y5=!",
        "TEMPLATE_CONTEXT_PROCESSORS": [
            "django.core.context_processors.request",
        ],
        "TEMPLATES": [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "DIRS": (os.path.join(ROOT, "template_dir"),),
                "OPTIONS": {
                    "debug": True,
                    "context_processors": [
                        "django.contrib.auth.context_processors.auth",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            }
        ],
        "JINJA2_TEMPLATES": [
            {
                "BACKEND": "django.template.backends.jinja2.Jinja2",
                "APP_DIRS": True,
                "DIRS": (
                    os.path.join(ROOT, "template_dir"),
                    os.path.join(ROOT, "templates"),  # or change app_dirname
                ),
                "OPTIONS": {
                    "extensions": [
                        "viewlet.loaders.jinja2_loader.ViewletExtension",
                    ],
                },
            }
        ],
        "JINJA2_ENVIRONMENT_OPTIONS": {"optimized": False},  # Coffin config
        "JINJA_CONFIG": {"autoescape": True},  # Jingo config
    }

    conf["MIDDLEWARE"] = conf.pop("MIDDLEWARE_CLASSES")

    conf.pop("TEMPLATE_DEBUG")
    conf.pop("TEMPLATE_CONTEXT_PROCESSORS")

    conf.update(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    )

    conf.update(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    )

    settings.configure(**conf)

    django.setup()

    from django.test.utils import get_runner

    test_runner = get_runner(settings)(verbosity=2, interactive=True)
    failures = test_runner.run_tests(["viewlet"])

    sys.exit(failures)


if __name__ == "__main__":
    main()
