# -*- coding: utf-8 -*-

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from ...models import FIELDS
from ...models import ModelA
from ...models import UNICODE_STRING


def create_test_data():
    try:
        User.objects.create_superuser(
            'admin',
            'admin@testapp.org',
            'adminpassword')
    except IntegrityError:
        pass

    User.objects.get_or_create(
        username='anyuser',
        is_active=True,
        is_staff=True,
        password='anyuserpassword'
    )

    for i in range(9):
        ma = ModelA()
        for field, data in FIELDS.items():
            setattr(ma, field, data['value'](i))
        ma.save()


class Command(BaseCommand):
    help = 'Administrative actions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--create-test-data',
            action='store_true',
            help='Create testdata.')

    def handle(self, *args, **options):
        if options['create_test_data']:
            create_test_data()
