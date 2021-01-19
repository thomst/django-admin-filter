# -*- coding: utf-8 -*-

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from django_admin_filter.models import FilterQuery
from django_admin_filter.settings import HISTORY_LIMIT
from ...models import FIELDS
from ...models import ModelA
from ...models import UNICODE_STRING

User = get_user_model()


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

    # create some model-items
    for i in range(9):
        ma = ModelA()
        for field, data in FIELDS.items():
            setattr(ma, field, data['value'](i))
        ma.save()

    # create some simple filterqueries
    content_type = ContentType.objects.get(model=ModelA.__name__.lower())
    for i in range(3 + HISTORY_LIMIT):
        fq = FilterQuery()
        fq.name = 'Filter {}'.format(i + 1)
        fq.user = User.objects.get(username='admin')
        fq.content_type = content_type
        fq.querydict = dict(auto=i+1)
        fq.persistent = True if i < 3 else False
        fq.save()


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
