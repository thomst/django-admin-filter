# -*- coding: utf-8 -*-

import uuid, os
from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _


UNICODE_STRING = 'ℋℌℍℎℏℐℑℒℓ'


class ModelA(models.Model):
    first = models.IntegerField()
    second = models.DecimalField(max_digits=5, decimal_places=2)
    third = models.CharField(max_length=24)
    forth = models.CharField(max_length=24)
