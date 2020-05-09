import re
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib import admin

from . import settings as app_settings
from .filterset import AdminFilterSet
from .models import FilterQuery


class CustomFilter(admin.SimpleListFilter):
    title = _('Custom Filters')
    template = 'django_admin_filter/custom_filter.html'
    parameter_name = 'filter_id'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.csrftoken = request.META.get('CSRF_COOKIE')
        self.filterset_class = AdminFilterSet.by_model(model)
        try:
            self.current_query = FilterQuery.objects.get(pk=self.value())
        except FilterQuery.DoesNotExist:
            self.current_query = None

    def queryset(self, request, queryset):
        if not self.current_query:
            return queryset

        return self.filterset_class(self.current_query.querydict, queryset).qs

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        model_name = model_admin.model.__name__.lower()
        params = dict(content_type__model=model_name, user=request.user)
        persistent = FilterQuery.objects.filter(persistent=True, **params)
        history = FilterQuery.objects.filter(persistent=False, **params)
        recent = history[:app_settings.HISTORY_LIMIT]
        return list(persistent) + list(recent)

    def choices(self, changelist):
        if self.lookup_choices:
            remove = self.used_parameters.keys()
            yield {
                'selected': not self.used_parameters,
                'query_string': changelist.get_query_string(remove=remove),
                'display': _('All'),
            }
        for query in self.lookup_choices:
            yield {
                'selected': self.current_query and self.current_query.id == query.id,
                'query_string': changelist.get_query_string(dict(filter_id=query.id)),
                'csrftoken': self.csrftoken,
                'filter': query,
            }
