=================================
Welcome to django-admin-filter
=================================

.. image:: https://travis-ci.com/thomst/django-admin-filter.svg?branch=master
   :target: https://travis-ci.com/thomst/django-admin-filter

.. image:: https://coveralls.io/repos/github/thomst/django-admin-filter/badge.svg?branch=master
   :target: https://coveralls.io/github/thomst/django-admin-filter?branch=master

.. image:: https://img.shields.io/badge/python-3.4%20%7C%203.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue
   :target: https://img.shields.io/badge/python-3.4%20%7C%203.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue
   :alt: python: 3.4, 3.5, 3.6, 3.7, 3.8

.. image:: https://img.shields.io/badge/django-1.11%20%7C%202.0%20%7C%202.1%20%7C%202.2%20%7C%203.0-orange
   :target: https://img.shields.io/badge/django-1.11%20%7C%202.0%20%7C%202.1%20%7C%202.2%20%7C%203.0-orange
   :alt: django: 1.11, 2.0, 2.1, 2.2, 3.0


Description
===========
Django-admin-filter is generic form-based filter for the django-admin-page.
It is based on django-filter. It provides a flexible and direct way to filter
the items of your changelist.


Installation
============
Install from pypi.org::

    pip install django-admin-filter

Add csvexport to your installed apps::

    INSTALLED_APPS = [
        'django_admin_filter',
        ...
    ]
