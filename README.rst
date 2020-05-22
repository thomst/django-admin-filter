=================================
Welcome to django-admin-filter
=================================

.. image:: https://api.travis-ci.org/thomst/django-admin-filter.svg?branch=master
   :target: https://travis-ci.org/github/thomst/django-admin-filter

.. image:: https://coveralls.io/repos/github/thomst/django-admin-filter/badge.svg?branch=master
   :target: https://coveralls.io/github/thomst/django-admin-filter?branch=master

.. image:: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue
   :target: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue
   :alt: python: 3.4, 3.5, 3.6, 3.7, 3.8

.. image:: https://img.shields.io/badge/django-2.2%20%7C%203.0-orange
   :target: https://img.shields.io/badge/django-2.2%20%7C%203.0-orange
   :alt: django: 1.11, 2.0, 2.1, 2.2, 3.0

.. _django-filter: https://github.com/carltongibson/django-filter
.. _django-filter-docs: https://django-filter.readthedocs.io/en/master/


Description
===========
Django-admin-filter is a generic form-based filter for the django-admin-page.
It is based on django-filter_. It provides a flexible and direct way to filter
the items of your changelist and to save and reuse your queries.


Installation
============
Install from pypi.org::

   pip install django-admin-filter


Configuration
=============
There are three things you need to do to use a custom filter-form for your model
in your admin changelist:


Add `django_admin_filter` to your `INSTALLED_APPS`::

   INSTALLED_APPS = [
      'django_admin_filter',
      ...
   ]


Add the `CustomFilter` to the `list_filter` of your ModelAdmin::

   from django_admin_filter.filters import CustomFilter

   class MyAdmin(admin.ModelAdmin):
      list_filter = [CustomFilter, ...]
      ...


And setup the filter-class you want to use with your model. This works exactly
as described in the django-filter-docs_. But to use your filter-class with the
django-admin-filter there is one thing to mind: Instead of subclass
`django_filters.FilterSet`::

   import django_filters

   class MyFilter(django_filters.FilterSet):
      ...

use the `AdminFilterSet`::

   from django_admin_filter.filterset import AdminFilterSet

   class MyFilter(AdminFilterSet):
      ...
