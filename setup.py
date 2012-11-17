#!/usr/bin/env python
import os
import codecs
from setuptools import setup, find_packages

version = __import__('viewlet').__version__

setup(
    name             = "django-viewlet",
    version          = version,

    description      = "Render template parts with extended cache control.",
    long_description = codecs.open(
        os.path.join(
            os.path.dirname(__file__),
            "README.rst"
        )
    ).read(),
    author           = "Jonas Lundberg",
    author_email     = "jonas@5monkeys.se",
    url              = "http://github.com/5monkeys/django-viewlet",
    download_url     = "https://github.com/5monkeys/django-viewlet/tarball/%s" % (version,),

    keywords         = ["django", "template", "cache", 'view', 'subview', 'decorator', 'refresh', 'invalidate'],
    classifiers      = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        'Topic :: Internet :: WWW/HTTP',
    ],

    zip_safe = False,
    packages = find_packages(exclude=["tests"]),
    include_package_data = False,

    dependency_links = [
    ],

    install_requires = [
    ],
)
