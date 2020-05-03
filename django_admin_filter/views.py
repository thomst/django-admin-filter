
from decimal import Decimal

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


def permission_required(func):
    def wrapper(self, request, **kwargs):
        permission = '{app_label}.view_{model}'.format(**kwargs)
        if not request.user.has_perm(permission):
            raise PermissionDenied
        return func(self, request, **kwargs)
    return wrapper


def setup(func):
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
    template_name = 'django_admin_filter/filter_query.html'
    model = Filter
    form_class = FilterForm
    object = None

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

    def get_querydict(self, query_form):
        empty = lambda v: v is str() or v is None
        data = query_form.cleaned_data
        querydict = dict((k, v) for k, v in data.items() if not empty(v))

        # FIXME: The django-filter does not differenciate decimals and integers.
        # That means all numbers come as decimals from the filter-forms and the
        # JSONField serializes each with an extra decimal-place. Used as params
        # the queryset filter-method works fine. But a decimal coming from as
        # urlquery won't work in django's changelists.
        # The long-term-fix would be a pull-request to django-filter.
        for k, v in querydict.copy().items():
            if isinstance(v, Decimal) and v % 1 == 0:
                querydict[k] = int(v)
        return querydict

    def form_valid(self, form, query_form):
        self.object = form.save(commit=False)
        self.object.querydict = self.get_querydict(query_form)
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
        url = reverse(url_pattern.format(**self.kwargs)) + '?' + self.object.urlquery
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
