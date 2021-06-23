
import re

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from django_admin_filter import apps
from django_admin_filter import settings as app_settings
from django_admin_filter.filters import CustomFilter
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


class AddPermission:
    def __init__(self, user, perm):
        self.user = user
        self.perm = perm

    def __enter__(self):
        self.user.user_permissions.add(self.perm)       

    def __exit__(self, type, value, traceback):
        self.user.user_permissions.remove(self.perm)


class FilterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data()

    def setUp(self):
        self.admin = get_user_model().objects.get(username='admin')
        self.anyuser = get_user_model().objects.get(username='anyuser')
        self.permission = Permission.objects.get(codename='can_handle_global_filterqueries')
        self.url = reverse('admin:testapp_modela_changelist')
        self.fq_url = '{}{}'.format(self.url, app_settings.URL_PATH)
        content_type = ContentType.objects.get(model=ModelA.__name__.lower())
        self.fq_params = dict(user=self.admin, content_type=content_type)
        self.queryset = FilterQuery.objects.filter(**self.fq_params)
        self.persistents = self.queryset.filter(persistent=True)
        self.history = self.queryset.filter(persistent=False)
        self.globals = self.queryset.filter(for_everyone=True)
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
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.check_content(response)

        for i in range(3):
            with AlterAppSettings(HISTORY_LIMIT=i, TRUNCATE_HISTORY=False):
                response = self.client.get(self.url)
                self.check_content(response)

    def test_02_filter_deletion(self):
        self.client.force_login(self.admin)
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
        self.client.force_login(self.admin)
        response = self.client.get(self.fq_url)
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        for field_name in self.querydict.keys():
            self.assertIn(field_name, content)

        # check if the for_everyone field is visible
        self.assertIn('<input type="checkbox" name="fq-for_everyone"', content)

        # use invalid url-keywords for app_label and model
        url = self.fq_url.replace('modela', 'modelx')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # load filter query form to update an existing filter query
        fq_id = FilterQuery.objects.filter(persistent=True, user=self.admin)[0].id
        url = '{}{}'.format(self.fq_url, fq_id)
        response = self.client.get(url, follow=True)
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Save as new and apply", content)
        for field_name in self.querydict.keys():
            self.assertIn(field_name, content)


    def test_05_post_filterquery_form(self):
        self.client.force_login(self.admin)
        # pass invalid form-data
        post_data = dict()
        post_data['save'] = True
        post_data['auto'] = 'foobar'
        response = self.client.post(self.fq_url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertIn('<ul class="errorlist"><li>Enter a number.</li></ul>', response.content.decode('utf8'))

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

    def test_06_get_filterquery_form_with_unprivileged_user(self):
        self.client.force_login(self.anyuser)

        # load edit global filter form - should fail
        fq = FilterQuery.objects.filter(for_everyone=True)[0]
        url = '{}{}/'.format(self.fq_url, fq.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # load edit admin filter form - should fail
        fq = FilterQuery.objects.filter(persistent=True, user=self.admin)[0]
        url = '{}{}/'.format(self.fq_url, fq.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # load filter form - check if for_everyone is hidden
        fq = FilterQuery.objects.filter(persistent=True, user=self.anyuser)[0]
        url = '{}{}/'.format(self.fq_url, fq.id)
        response = self.client.get(url)
        content = response.content.decode('utf-8')
        self.assertIn('<input type="hidden" name="fq-for_everyone"', content)

        # for_everyone should be visible if user gets extra permission
        with AddPermission(self.anyuser, self.permission):
            fq = FilterQuery.objects.filter(persistent=True, user=self.anyuser)[0]
            url = '{}{}/'.format(self.fq_url, fq.id)
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            self.assertIn('<input type="checkbox" name="fq-for_everyone"', content)

    def test_05_post_filterquery_form_with_unprivileged_user(self):
        self.client.force_login(self.anyuser)

        # try to create filterquery with for_everyone - should fail
        post_data = dict()
        post_data['save'] = True
        post_data['fq-for_everyone'] = True
        response = self.client.post(self.fq_url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 403)

        # give user permission and create filterquery with for_everyone
        with AddPermission(self.anyuser, self.permission):
            response = self.client.post(self.fq_url, data=post_data, follow=True)
            self.assertEqual(response.status_code, 200)
            fq = FilterQuery.objects.latest('created')
            redirect_url = '{}?filter_id={}'.format(self.url, fq.id)
            self.assertEqual(response.redirect_chain[0][0], redirect_url)
            self.assertTrue(fq.persistent)


    def test_06_custom_filter_form_with_unprivileged_user(self):
        self.client.force_login(self.anyuser)

        # load changelist - check custom filter
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        for fq in self.globals.all():
            self.assertIn(fq.name, content)
            self.assertIn(fq.description, content)
            self.assertIn('?filter_id={}'.format(fq.id), content)
            # edit and delete links shouldn't be rendered
            self.assertNotIn('{}{}/'.format(app_settings.URL_PATH, fq.id), content)

        # give user permission and do it again
        with AddPermission(self.anyuser, self.permission):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            content = response.content.decode('utf-8')
            for fq in self.globals.all():
                self.assertIn(fq.name, content)
                self.assertIn(fq.description, content)
                self.assertIn('?filter_id={}'.format(fq.id), content)
                # edit and delete links should be rendered now
                self.assertIn('{}{}/'.format(app_settings.URL_PATH, fq.id), content)

    def test_07_valid_content_type_header_in_request(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.fq_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['content-type'].startswith('text/html'))

