
import html.parser
from decimal import Decimal

from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import BaseCreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .filterset import REGISTRY
from .models import Filter
from .forms import FilterForm


def is_empty(value):
    """
    Filter out those form-fields without any input-data.
    """
    return value is str() or value is None or value == list()



def prepare_value(value):
    """
    Prepare the values coming from a filter-form.
    """
    # The cleaned_data provides special unicode characters as html-escaped.
    if isinstance(value, str):
        parser = html.parser.HTMLParser()
        return parser.unescape(value)
    # For any reason the django-filter's form provides all numbers as decimals -
    # even for IntegerFields. The queryset-object doesn't seem to be bothered
    # by decimals as filter-values. But the admin-changelist doesn't accept them
    # in the url-query.
    # This should be fixed in django-filter though.
    elif isinstance(value, Decimal) and value % 1 == 0:
        return int(value)
    else:
        return value


def get_querydict(queryform):
    """
    Get the querydict from a filter-form.
    """
    data = queryform.cleaned_data
    querydict = dict((k, prepare_value(v)) for k, v in data.items() if not is_empty(v))
    return querydict


def permission_required(func):
    """
    Decorator for view-methods to check permission to view the filtered items.
    """
    def wrapper(self, request, **kwargs):
        permission = '{app_label}.view_{model}'.format(**kwargs)
        if not request.user.has_perm(permission):
            raise PermissionDenied
        return func(self, request, **kwargs)
    return wrapper


def setup(func):
    """
    Extract the contenttype from url-paramerters and setup the filter-class.
    """
    def wrapper(self, request, **kwargs):
        try:
            self.content_type = ContentType.objects.get(**kwargs)
        except ContentType.DoesNotExist:
            raise Http404(_(
                "No model '{model}' in app '{app_label}'".format(**kwargs)
            ))
        else:
            ct_model = self.content_type.model_class()
        try:
            self.filter_class = REGISTRY[ct_model]
        except KeyError:
            raise ImproperlyConfigured(_(
                "Missing filter-class for Model '{model}'".format(**kwargs)
            ))
        return func(self, request, **kwargs)
    return wrapper


class FilterView(LoginRequiredMixin, TemplateResponseMixin, BaseCreateView):
    """
    View to add and delete Filters.
    """
    template_name = 'django_admin_filter/filter_query.html'
    model = Filter
    form_class = FilterForm
    object = None

    @permission_required
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.user == self.request.user:
            raise PermissionDenied
        self.object.delete()
        return JsonResponse(dict())

    @setup
    @permission_required
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @setup
    @permission_required
    def post(self, *args, **kwargs):
        form = self.get_form()
        query_form = self.get_query_form()

        if form.is_valid() and query_form.is_valid():
            return self.form_valid(form, query_form)
        else:
            return self.form_invalid(form, query_form)

    def form_valid(self, form, query_form):
        self.object = form.save(commit=False)
        self.object.querydict = get_querydict(query_form)
        self.object.content_type = self.content_type
        self.object.persistent = 'save' in self.request.POST
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form, query_form):
        context = self.get_context_data(form=form, query_form=query_form)
        return self.render_to_response(context)

    def get_success_url(self):
        url_pattern = 'admin:{app_label}_{model}_changelist'
        query = '?filter_id={}&{}'.format(self.object.id, self.object.urlquery)
        url = reverse(url_pattern.format(**self.kwargs)) + query
        return url

    def get_query_form(self):
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST
        else:
            data = dict()
        filter = self.filter_class(data, prefix='query')
        return filter.form

    def get_context_data(self, **kwargs):
        query_form = self.get_query_form()
        extra_context = dict(query_form=query_form)
        extra_context.update(kwargs)
        return super().get_context_data(**extra_context)
