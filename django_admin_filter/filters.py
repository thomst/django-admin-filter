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
        self.current_filter = None
        if self.value():
            self.current_filter = Filter.objects.get(pk=self.value())
            self.used_parameters.update(self.current_filter.querydict)

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

    def get_query_string(self, filter):
        add = filter.querydict
        add[self.parameter_name] = filter.id
        remove = set()
        if self.current_filter and not self.current_filter.id == filter.id:
            remove = set(self.current_filter.querydict.keys())
            remove -= set(filter.querydict.keys())
        return add, list(remove)

    def choices(self, changelist):
        if self.lookup_choices:
            remove = self.used_parameters.keys()
            yield {
                'selected': not self.used_parameters,
                'query_string': changelist.get_query_string(remove=remove),
                'display': _('All'),
            }
        for filter in self.lookup_choices:
            add, remove = self.get_query_string(filter)
            yield {
                'selected': self.current_filter and self.current_filter.id == filter.id,
                'query_string': changelist.get_query_string(add, remove),
                'filter': filter,
            }
