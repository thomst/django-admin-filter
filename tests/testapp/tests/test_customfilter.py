
import re

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django_admin_filter import apps
from django_admin_filter import settings as app_settings
from django_admin_filter.filters import CustomFilter
from django_admin_filter.views import FilterQueryView
from django_admin_filter.models import FilterQuery

from ..models import ModelA
from ..models import UNICODE_STRING
from ..models import FIELDS
from ..management.commands.testapp import create_test_data
from .. import urls


class AlterAppSettings:
    def __init__(self, **kwargs):
        self.settings = kwargs
        self.origin = dict()

    def __enter__(self):
        for setting, value in self.settings.items():
            self.origin[setting] = getattr(app_settings, setting)
            setattr(app_settings, setting, value)

    def __exit__(self, type, value, traceback):
        for setting, value in self.origin.items():
            setattr(app_settings, setting, value)


class FilterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data()

    def setUp(self):
        self.admin = User.objects.get(username='admin')
        self.client.force_login(self.admin)
        self.url = reverse('admin:testapp_modela_changelist')
        self.fq_url = '{}{}'.format(self.url, app_settings.URL_PATH)
        content_type = ContentType.objects.get(model=ModelA.__name__.lower())
        self.fq_params = dict(user=self.admin, content_type=content_type)
        self.queryset = FilterQuery.objects.filter(**self.fq_params)
        self.persistents = self.queryset.filter(persistent=True)
        self.history = self.queryset.filter(persistent=False)
        self.querydict = dict()
        index = 4
        for field, data in FIELDS.items():
            self.querydict[field] = data['filters']['exact'](index)
            for filter, data_gen in data['filters'].items():
                if filter == 'exact': continue
                self.querydict[field + '__' + filter] = data_gen(index)

    def check_content(self, response):
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn(CustomFilter.title, content)
        self.assertIn('href="{}"'.format(app_settings.URL_PATH), content)
        for fq in self.persistents.all():
            self.assertIn(fq.name, content)
            self.assertIn(fq.description, content)
            self.assertIn('{}{}/'.format(app_settings.URL_PATH, fq.id), content)
        for fq in self.history.all()[:app_settings.HISTORY_LIMIT]:
            self.assertIn(fq.name, content)
            self.assertIn(fq.description, content)
        for fq in self.history.all()[app_settings.HISTORY_LIMIT:]:
            self.assertNotIn(fq.name, content)

    def test_01_custom_filter_form(self):
        response = self.client.get(self.url)
        self.check_content(response)

        for i in range(3):
            with AlterAppSettings(HISTORY_LIMIT=i, TRUNCATE_HISTORY=False):
                response = self.client.get(self.url)
                self.check_content(response)

    def test_02_filter_deletion(self):
        fq = self.persistents.all()[0]
        url = '{}{}/'.format(self.fq_url, fq.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(FilterQuery.DoesNotExist, FilterQuery.objects.get, pk=fq.id)

    def test_03_create_filterquery(self):
        # check name-generation with and without timezone-awareness
        for bool in [True, False]:
            with self.settings(USE_TZ=bool):
                fq = FilterQuery(**self.fq_params)
                fq.save()
                self.assertTrue(re.match(r'^Filter from [0-9/-: ]+$', fq.name))

        # check description-generation
        description = list()
        querydict = dict()
        for field, value in self.querydict.items():
            querydict[field] = value
            description.append('{} = {}'.format(field, value))
            fq = FilterQuery(**self.fq_params, querydict=querydict)
            fq.save()
            for line in description:
                self.assertIn(line, fq.description)

        # check history-truncation
        with AlterAppSettings(TRUNCATE_HISTORY=True):
            for i in range(3):
                fq = FilterQuery(**self.fq_params)
                fq.save()
                history = self.history.all()
                self.assertEqual(len(history), app_settings.HISTORY_LIMIT)

    def test_04_get_filterquery_form(self):
        response = self.client.get(self.fq_url)
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        for field_name in self.querydict.keys():
            self.assertIn(field_name, content)

    def test_05_post_filterquery_form(self):
        # create filter via save and apply
        for action in ['save', 'apply']:
            post_data = self.querydict.copy()
            post_data[action] = True
            response = self.client.post(self.fq_url, data=post_data, follow=True)
            self.assertEqual(response.status_code, 200)
            fq = FilterQuery.objects.latest('created')
            redirect_url = '{}?filter_id={}'.format(self.url, fq.id)
            self.assertEqual(response.redirect_chain[0][0], redirect_url)
            self.assertTrue(fq.persistent == (action is 'save'))
