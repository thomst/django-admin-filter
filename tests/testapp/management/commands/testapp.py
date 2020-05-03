# -*- coding: utf-8 -*-

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from ...models import ModelA


def create_test_data():
    try:
        User.objects.create_superuser(
            'admin',
            'admin@testapp.org',
            'adminpassword')
    except IntegrityError:
        pass

    for i in range(7):
        ma = ModelA()
        ma.first = i
        ma.second = i * 2
        ma.third = i * 3
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
