#!/usr/bin/env python
# coding=utf-8
"""
Based partly on Django's own ``setup.py``.
"""
import codecs
from distutils.command.install_data import install_data
import os
from setuptools import setup, find_packages
import sys

version = __import__("viewlet").__version__


class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is at:
    #   /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific
    # fix for this in distutils.command.install_data#306. It fixes install_lib
    # but not install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to
        # the fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}


setup(
    name="django-viewlet",
    version=version,
    description="Render template parts with extended cache control.",
    long_description=codecs.open(
        os.path.join(
            os.path.dirname(__file__),
            "README.rst"
        )
    ).read(),
    author="Jonas Lundberg",
    author_email="jonas@5monkeys.se",
    url="http://github.com/5monkeys/django-viewlet",
    download_url="https://github.com/5monkeys/django-viewlet/tarball/%s" % (version,),
    keywords=["django", "template", "cache", "view", "subview", "decorator", "refresh", "invalidate"],
    platforms=["any"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Django",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
    packages=find_packages(),
    include_package_data=False,
    dependency_links=[
    ],
    install_requires=[
    ],
    tests_require=['Django', 'Coffin', 'Jinja2'],
    test_suite='run_tests.main',
    cmdclass=cmdclasses,
)
