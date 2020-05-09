# -*- coding: utf-8 -*-

import uuid, os
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _


UNICODE_STRING = 'ℋ/ℌ=ℍ&ℎ?ℏ'


FIELDS = dict(
    auto = dict(
        field = models.AutoField(primary_key=True),
        value = lambda i: i,
        filters = ['exact', 'lt', 'gt', 'in'],
    ),
    char = dict(
        field = models.CharField(max_length=24),
        value = lambda i: UNICODE_STRING[:i],
        filters = ['exact', 'contains', 'icontains'],
    ),
    boolean = dict(
        field = models.BooleanField(),
        value = lambda i: [True, False][i % 2],
        filters = ['exact'],
    ),
    nullboolean = dict(
        field = models.NullBooleanField(),
        value = lambda i: [True, False, None][i % 3],
        filters = ['exact', 'isnull'],
    ),
    date = dict(
        field = models.DateField(),
        value = lambda i: (datetime.utcfromtimestamp(0) + timedelta(days=i)).date(),
        filters = ['exact', 'day__gt', 'day__lt', 'range'],
    ),
    datetime = dict(
        field = models.DateTimeField(),
        value = lambda i: datetime.utcfromtimestamp(0) + timedelta(days=i),
        filters = ['exact', 'day__gt', 'day__lt', 'range'],
    ),
    time = dict(
        field = models.TimeField(),
        value = lambda i: (datetime.utcfromtimestamp(0) + timedelta(hours=i)).time(),
        filters = ['exact', 'hour__gt', 'hour__lt'],
    ),
    duration = dict(
        field = models.DurationField(),
        value = lambda i: timedelta(hours=i),
        filters = ['exact'],
    ),
    integer = dict(
        field = models.IntegerField(),
        value = lambda i: i,
        filters = ['exact', 'lt', 'gt', 'in', 'range'],
    ),
    float = dict(
        field = models.FloatField(),
        value = lambda i:  i/5.0,
        filters = ['exact', 'lt', 'gt', 'in', 'range'],
    ),
    decimal = dict(
        field = models.DecimalField(max_digits=5, decimal_places=2),
        value = lambda i: i/5.0,
        filters = ['exact', 'lt', 'gt', 'in', 'range'],
    ),
)


class BaseModel(models.Model):
    class Meta:
        abstract = True


model_attrs = dict(__module__=BaseModel.__module__)
model_attrs.update(dict([(k, v['field']) for k, v in FIELDS.items()]))
ModelA = type('ModelA', (BaseModel,), model_attrs)


# class ModelA(models.Model):
#     auto = models.AutoField(primary_key=True)
#     char = models.CharField(max_length=24)
#     text = models.TextField()
#     boolean = models.BooleanField()
#     date = models.DateField()
#     datetime = models.DateTimeField()
#     time = models.TimeField()
#     duration = models.DurationField()
#     decimal = models.DecimalField(max_digits=5, decimal_places=2)
#     smallinteger = models.SmallIntegerField()
#     integer = models.IntegerField()
#     positiveinteger = models.PositiveIntegerField()
#     positivesmallinteger = models.PositiveSmallIntegerField()
#     float = models.FloatField()
#     nullboolean = models.NullBooleanField()
#     slug = models.SlugField()
#     email = models.EmailField()
#     filepath = models.FilePathField()
#     url = models.URLField()
#     genericipaddress = models.GenericIPAddressField()
#     uuid = models.UUIDField()
