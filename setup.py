#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding="utf-8") as file:
        return file.read()


version = __import__("django_admin_filter").__version__
if '-dev' in version:
    dev_status = 'Development Status :: 3 - Alpha'
elif '-beta' in version:
    dev_status = 'Development Status :: 4 - Beta'
else:
    dev_status = 'Development Status :: 5 - Production/Stable'


setup(
    name="django-admin-filter",
    version=version,
    description="A generic filter for the django-admin-page based on django-filter.",
    long_description=read("README.rst"),
    author="Thomas Leichtfuß",
    author_email="thomas.leichtfuss@posteo.de",
    url="https://github.com/thomst/django-admin-filter",
    license="BSD License",
    platforms=["OS Independent"],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "Django>=2.2",
        'django-filter>=2.2',
        'jsonfield>=3.1.0',
    ],
    classifiers=[
        dev_status,
        "Framework :: Django",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    zip_safe=True,
)
