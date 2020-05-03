from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib import admin
from .models import Filter


class CustomFilter(admin.SimpleListFilter):
    title = _('Custom Filters')
    template = 'django_admin_filter/custom_filter.html'
    parameter_name = 'filter_id'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        if self.value():
            self.filter = Filter.objects.get(pk=self.value())
        else:
            self.filter = None

    def queryset(self, request, queryset):
        return queryset

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        model_name = model_admin.model.__name__.lower()
        params = dict(content_type__model=model_name, user=request.user)
        persistent = Filter.objects.filter(persistent=True, **params)
        history = Filter.objects.filter(persistent=False, **params)
        return list(persistent) + list(history)

    def choices(self, changelist):
        if self.lookup_choices:
            remove = self.filter.query.keys() if self.filter else list()
            yield {
                'selected': self.value() is None,
                'query_string': changelist.get_query_string(remove=remove),
                'display': _('All'),
            }
        for filter in self.lookup_choices:
            yield {
                'selected': self.value() == str(filter.id),
                'query_string': changelist.get_query_string(filter.query),
                'filter': filter,
            }
