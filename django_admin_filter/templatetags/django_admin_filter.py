# -*- coding: utf-8 -*-
from django.template import Library
from .. import settings


register = Library()


@register.simple_tag
def urlpath():
    return settings.URL_PATH


@register.filter
def persistent_everyone(filter):
    return [f for f in filter[1:] if f['filter'].persistent and f['filter'].for_everyone]


@register.filter
def persistent_personal(filter):
    return [f for f in filter[1:] if f['filter'].persistent and not f['filter'].for_everyone]


@register.filter
def history(filter):
    return [f for f in filter[1:] if not f['filter'].persistent]
