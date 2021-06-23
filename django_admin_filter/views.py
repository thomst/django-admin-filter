import html.parser
from decimal import Decimal

from django import forms
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.text import format_lazy
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import BaseCreateView, BaseUpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .filterset import AdminFilterSet
from .models import FilterQuery
from .forms import FilterForm


def can_view_related_model(func):
    """
    Decorator for view-methods to check permission to view the filtered items.
    """
    def wrapper(self, request, **kwargs):
        permission = '{app_label}.view_{model}'.format(**kwargs)
        if not request.user.has_perm(permission):
            raise PermissionDenied
        return func(self, request, **kwargs)
    return wrapper


def can_handle_filterquery(func):
    """
    Decorator to check the permission to delete or update a specific filterquery.
    """
    def wrapper(self, request, **kwargs):
        obj = self.get_object()
        is_owner = obj.user == self.request.user
        can_handle = obj.for_everyone and obj.has_global_perm(self.request.user)
        if not is_owner and not can_handle:
            raise PermissionDenied

        return func(self, request, **kwargs)
    return wrapper


def setup_filterclass(func):
    """
    Extract the contenttype from url-paramerters and setup the filter-class.
    """
    def wrapper(self, request, **kwargs):
        params = dict(app_label=kwargs['app_label'], model=kwargs['model'])
        try:
            self.content_type_obj = ContentType.objects.get(**params)
        except ContentType.DoesNotExist:
            msg = format_lazy(_("No model '{model}' in app '{app_label}'"), **params)
            raise Http404(msg)
        else:
            ct_model = self.content_type_obj.model_class()
            self.filterset_class = AdminFilterSet.by_model(ct_model)
        return func(self, request, **kwargs)
    return wrapper


class BaseFilterQueryView(LoginRequiredMixin, TemplateResponseMixin):
    """
    View to add and delete Filters.
    """
    template_name = 'django_admin_filter/filter_query.html'
    model = FilterQuery
    form_class = FilterForm
    prefix = 'fq'
    object = None

    def post(self, *args, **kwargs):
        form = self.get_form()
        query_form = self.get_query_form()

        if form.is_valid() and query_form.is_valid():
            return self.form_valid(form, query_form)
        else:
            return self.form_invalid(form, query_form)

    def get_querydict(self):
        # TODO: Filter out FILTERS_NULL_CHOICE_VALUE for ChoiceFilter and
        # 'unknown' for BooleanFields.
        field_names = self.filterset_class().form.fields.keys()
        querydict = dict(
            (k, v) for k, v in self.request.POST.items()
            if k in field_names and not v is str()
        )
        return querydict

    def form_valid(self, form, query_form):
        self.object = form.save(commit=False)
        if 'save' not in self.request.POST :
            self.object.id = None
        self.object.querydict = self.get_querydict()
        self.object.content_type = self.content_type_obj
        self.object.persistent = 'save' in self.request.POST or 'save_new' in self.request.POST
        self.object.for_everyone = self.object.for_everyone and self.object.persistent
        self.object.user = self.request.user
        self.object.save()

        # check extra permission for global filterqueries
        if self.object.for_everyone and not self.object.has_global_perm(self.request.user):
            raise PermissionDenied

        return HttpResponseRedirect(self.get_success_url()) 

    def form_invalid(self, form, query_form):
        context = self.get_context_data(form=form, query_form=query_form)
        return self.render_to_response(context)

    def get_success_url(self):
        url_pattern = 'admin:{app_label}_{model}_changelist'
        query = '?filter_id={}'.format(self.object.id)
        url = reverse(url_pattern.format(**self.kwargs)) + query
        return url

    def get_form(self):
        form = super().get_form()
        # hide the for_everyone field if user has no permission
        if not FilterQuery.has_global_perm(self.request.user):
            form.fields['for_everyone'].widget = forms.HiddenInput()
        return form

    def get_query_form(self):
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST
        else:
            data = self.object.querydict if self.object else dict()
        filter = self.filterset_class(data)
        return filter.form

    def get_context_data(self, **kwargs):
        query_form = self.get_query_form()
        extra_context = dict(query_form=query_form)
        extra_context.update(kwargs)
        return super().get_context_data(**extra_context)


class CreateFilterQueryView(BaseFilterQueryView, BaseCreateView):
    @setup_filterclass
    @can_view_related_model
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @setup_filterclass
    @can_view_related_model
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateFilterQueryView(BaseFilterQueryView, BaseUpdateView):
    @setup_filterclass
    @can_view_related_model
    @can_handle_filterquery
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @setup_filterclass
    @can_view_related_model
    @can_handle_filterquery
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    @can_view_related_model
    @can_handle_filterquery
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        response = dict(id=self.object.id)
        self.object.delete()
        return JsonResponse(response)
