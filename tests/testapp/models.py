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
        filters = {
            'exact': lambda i: str(i),
            'lt': lambda i: str(i),
            'gt': lambda i: str(i),
            'in': lambda i: ','.join(str(v) for v in range(i)),
            'range': lambda i: '0,{}'.format(i),
        },
    ),
    char = dict(
        field = models.CharField(max_length=24),
        value = lambda i: UNICODE_STRING[:i],
        filters = {
            'exact': lambda i: UNICODE_STRING[:i],
            'contains': lambda i: UNICODE_STRING[i],
            'icontains': lambda i: UNICODE_STRING[i],
        },
    ),
    boolean = dict(
        field = models.BooleanField(),
        value = lambda i: [True, False][i % 2],
        filters = {
            'exact': lambda i: [True, False][i % 2],
        },
    ),
    date = dict(
        field = models.DateField(),
        value = lambda i: (datetime.utcfromtimestamp(0) + timedelta(days=i)).date(),
        filters = {
            'exact': lambda i: str((datetime.utcfromtimestamp(0) + timedelta(days=i)).date()),
            'day__gt': lambda i: str(i),
            'day__lt': lambda i: str(i),
            'range': lambda i: '{},{}'.format((datetime.utcfromtimestamp(0) + timedelta(days=0)).date(), (datetime.utcfromtimestamp(0) + timedelta(days=i)).date()),
        },
    ),
    datetime = dict(
        field = models.DateTimeField(),
        value = lambda i: datetime.utcfromtimestamp(0) + timedelta(days=i),
        filters = {
            'exact': lambda i: str((datetime.utcfromtimestamp(0) + timedelta(days=i))),
            'day__gt': lambda i: str(i),
            'day__lt': lambda i: str(i),
            'range': lambda i: '{},{}'.format(datetime.utcfromtimestamp(0) + timedelta(days=0), datetime.utcfromtimestamp(0) + timedelta(days=i)),
        },
    ),
    time = dict(
        field = models.TimeField(),
        value = lambda i: (datetime.utcfromtimestamp(0) + timedelta(hours=i)).time(),
        filters = {
            'exact': lambda i: str((datetime.utcfromtimestamp(0) + timedelta(days=i)).time()),
            'hour__gt': lambda i: str(i),
            'hour__lt': lambda i: str(i),
            'range': lambda i: '{},{}'.format((datetime.utcfromtimestamp(0) + timedelta(days=0)).time(), (datetime.utcfromtimestamp(0) + timedelta(days=i)).time()),
        },
    ),
    duration = dict(
        field = models.DurationField(),
        value = lambda i: timedelta(hours=i),
        filters = {
            'exact': lambda i: str(i),
        },
    ),
    integer = dict(
        field = models.IntegerField(),
        value = lambda i: i,
        filters = {
            'exact': lambda i: str(i),
            'lt': lambda i: str(i),
            'gt': lambda i: str(i),
            'in': lambda i: ','.join(str(v) for v in range(i)),
            'range': lambda i: '0,{}'.format(i),
        },
    ),
    float = dict(
        field = models.FloatField(),
        value = lambda i:  i/5.0,
        filters = {
            'exact': lambda i: str(i/5.0),
            'lt': lambda i: str(i/5.0),
            'gt': lambda i: str(i/5.0),
            'in': lambda i: ','.join(str(v) for v in range(i)),
        },
    ),
    decimal = dict(
        field = models.DecimalField(max_digits=5, decimal_places=2),
        value = lambda i: i/5.0,
        filters = {
            'exact': lambda i: str(i/5.0),
            'lt': lambda i: str(i/5.0),
            'gt': lambda i: str(i/5.0),
            'in': lambda i: ','.join(str(v) for v in range(i)),
        },
    ),
)


class BaseModel(models.Model):
    class Meta:
        abstract = True


model_attrs = dict(__module__=BaseModel.__module__)
model_attrs.update(dict([(k, v['field']) for k, v in FIELDS.items()]))
ModelA = type('ModelA', (BaseModel,), model_attrs)
