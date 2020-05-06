# -*- coding: utf-8 -*-

from django.contrib import admin
from django_admin_filter.filters import CustomFilter
from .models import ModelA
from .filters import ModelAFilter


@admin.register(ModelA)
class ModelAAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ModelA._meta.get_fields()]
    list_filter = [CustomFilter] + [f.name for f in ModelA._meta.get_fields()]
