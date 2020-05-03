# -*- coding: utf-8 -*-
from django.template import Library


register = Library()


@register.filter
def persistent(filter):
    return [f for f in filter[1:] if f['filter'].persistent]


@register.filter
def history(filter):
    return [f for f in filter[1:] if not f['filter'].persistent]
