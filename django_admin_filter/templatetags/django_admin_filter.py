# -*- coding: utf-8 -*-
from django.template import Library
from .. import settings


register = Library()


@register.simple_tag
def urlpath():
    return settings.URL_PATH


@register.filter
def persistent(filter):
    return [f for f in filter[1:] if f['filter'].persistent]


@register.filter
def history(filter):
    return [f for f in filter[1:] if not f['filter'].persistent]
