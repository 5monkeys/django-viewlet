#!/usr/bin/env python
# coding=utf-8
import os
import sys


if __name__ == '__main__':
    sys.path.append(os.path.dirname(__file__))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viewlet.test_settings')

    from django.conf import settings
    from django.test.utils import get_runner

    test_runner = get_runner(settings)(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['viewlet'])

    sys.exit(failures)
