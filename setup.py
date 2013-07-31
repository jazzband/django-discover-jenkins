#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys

LONG_DESCRIPTION = open('README.md').read()


def get_author_and_version(package):
    """
    Return package author and version as listed in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    author = re.search("__author__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    version = re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    return author, version


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


author, version = get_author_and_version('discover_jenkins')


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()


setup(
    name='django-discover-runner',
    version=version,
    description="A minimal fork of django-jenkins designed to work with the "
                "discover runner, made with simplicity in mind",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=['django', 'discover', 'runner', 'jenkins', 'hudson'],
    author=author,
    author_email='brandon@lincolnloop.com',
    url='https://github.com/lincolnloop/django-discover-jenkins',
    license='BSD',
    packages=get_packages('discover_jenkins'),
    include_package_data=True,
    zip_safe=False,
)
