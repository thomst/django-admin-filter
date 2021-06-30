=================================
Welcome to django-admin-filter
=================================

.. image:: https://api.travis-ci.org/thomst/django-admin-filter.svg?branch=master
   :target: https://travis-ci.org/github/thomst/django-admin-filter

.. image:: https://coveralls.io/repos/github/thomst/django-admin-filter/badge.svg?branch=master
   :target: https://coveralls.io/github/thomst/django-admin-filter?branch=master

.. image:: https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue
   :target: https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue
   :alt: python: 3.5, 3.6, 3.7, 3.8

.. image:: https://img.shields.io/badge/django-2.2%20%7C%203.0%20%7C%203.1%20%7C%203.2-orange
   :target: https://img.shields.io/badge/django-2.2%20%7C%203.0%20%7C%203.1%20%7C%203.2-orange
   :alt: django: 2.2, 3.0, 3.1, 3.2

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


Setup
=====
There are a few things you need to do to use a custom filter-form for your model
in your admin changelist:


Add `django_admin_filter` to your `INSTALLED_APPS`::

   INSTALLED_APPS = [
      'django_admin_filter',
      ...
   ]


Include the django_admin_filter.urls into your project urlpatterns. The
django_admin_filter.urls must precede the admin.site.urls::

   urlpatterns = [
      path('admin/', include('django_admin_filter.urls')),
      path('admin/', admin.site.urls),
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


Configuration
=============
django_admin_filter defines some settings by its own. These settings and their
default values are::

   ADMIN_FILTER_HISTORY_LIMIT = 3
   ADMIN_FILTER_TRUNCATE_HISTORY = True
   ADMIN_FILTER_URL_PATH = 'filter/'

ADMIN_FILTER_HISTORY_LIMIT
--------------------------
Filter queries that are not saved but only applied will be kept in the history
section of the custom filter. The HISTORY_LIMIT setting defines how many applied
filter queries will be kept. If you do not want to have a history of your
applied queries at all set this setting to 0.


ADMIN_FILTER_TRUNCATE_HISTORY
-----------------------------
By default applied filters that are beyond the scope of the filter history will
be delete automatically from the database. Set this setting to False if you want
to keep them for any reason.

ADMIN_FILTER_URL_PATH
---------------------
By default the route for the filter query form will be composed as follows::

   <app-label>/<model>/filter/[<pk>]

If this does not work with your project you can alter the "filter/" part by
using the ADMIN_FILTER_URL_PATH setting.


Usage
=====
The CustomFilter will show up on the right with all the other list filters. It
allows you to create new queries - based on your AdminFilterSet - or apply
existing queries - either recent ones from the history, or those you created.
It is also possible to create globel filter queries that can be used by every
user. To do so a user must have an extra permission defined with the FilterQuery
model::

   "Can handle global FilterQueries"

Users with this permission can commonly create edit and delete global filters.