
import re

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

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
        self.persistents = list(FilterQuery.objects.filter(persistent=True))
        self.history = list(FilterQuery.objects.filter(persistent=False))
        self.queryfields = list()
        for field, data in FIELDS.items():
            self.queryfields.append(field)
            for filter in data['filters']:
                if filter == 'exact': continue
                self.queryfields.append(field + '__' + filter)

    def check_content(self, response):
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn(CustomFilter.title, content)
        self.assertIn('href="{}"'.format(app_settings.URL_PATH), content)
        for fq in self.persistents:
            self.assertIn(fq.name, content)
            self.assertIn(fq.description, content)
            self.assertIn('{}{}/'.format(app_settings.URL_PATH, fq.id), content)
        for fq in self.history[:app_settings.HISTORY_LIMIT]:
            self.assertIn(fq.name, content)
            self.assertIn(fq.description, content)
        for fq in self.history[app_settings.HISTORY_LIMIT:]:
            self.assertNotIn(fq.name, content)

    def test_01_custom_filter_form(self):
        with self.settings(CSRF_USE_SESSIONS=True):
            response = self.client.get(self.url)
            self.check_content(response)

        with self.settings(CSRF_USE_SESSIONS=False):
            response = self.client.get(self.url)
            self.check_content(response)

        for i in [2, 1, 0]:
            with AlterAppSettings(HISTORY_LIMIT=i):
                response = self.client.get(self.url)
                self.check_content(response)

    def test_02_filter_deletion(self):
        fq = self.persistents[0]
        url = '{}{}{}/'.format(self.url, app_settings.URL_PATH, fq.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(FilterQuery.DoesNotExist, FilterQuery.objects.get, pk=fq.id)

    def test_03_get_filterquery_form(self):
        url = '{}{}'.format(self.url, app_settings.URL_PATH)
        response = self.client.get(url)
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        for field_name in self.queryfields:
            self.assertIn(field_name, content)

    def test_04_create_filterquery(self):
        url = '{}{}'.format(self.url, app_settings.URL_PATH)
        field_data = dict()

        # setup field-data for form-fields
        for field in self.queryfields:
            field_data[field] = str()

        # Create one filter-query using 'save' and without name-parameter:
        # TODO: check name-generation with USE_TZ=True
        post_data = field_data.copy()
        post_data['save'] = True
        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        name_pattern = r'^Filter from [0-9/: ]+$'
        fq = FilterQuery.objects.get(name__regex=name_pattern)
        self.assertTrue(fq.persistent)

        # create other filter-queries using 'apply' and check their description
        # TODO: create some real filter-values, not only numbers
        post_data = field_data.copy()
        post_data['apply'] = True
        description = list()
        name_field = '{}-name'.format(FilterQueryView.prefix)
        for i in range(1, 6):
            name = 'TestFilter ' + str(i)
            description.append('{} = {}'.format(self.queryfields[i], i))
            post_data[name_field] = name
            post_data[self.queryfields[i]] = str(i)
            response = self.client.post(url, data=post_data, follow=True)
            self.assertEqual(response.status_code, 200)
            fq = FilterQuery.objects.get(name=name)
            redirect_url = '{}?filter_id={}'.format(self.url, fq.id)
            self.assertEqual(response.redirect_chain[0][0], redirect_url)
            self.assertFalse(fq.persistent)
            for line in description:
                self.assertIn(line, fq.description)
