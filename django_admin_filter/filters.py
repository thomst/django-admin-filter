import re
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
        csrftoken = re.findall(r'csrftoken=(\w+)', request.headers['Cookie'])
        self.csrftoken = csrftoken[0] if csrftoken else None
        self.current_filter = None
        if self.value():
            try:
                self.current_filter = Filter.objects.get(pk=self.value())
            except Filter.DoesNotExist:
                pass
            else:
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
        history_limit = getattr(settings, 'ADMIN_FILTER_HISTORY_LIMIT', 5)
        recent = history[:history_limit]
        history.exclude(id__in=[f.id for f in recent]).delete()
        return list(persistent) + list(recent)

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
                'delete_path': 'c/filter/{}'.format(filter.id),
                'csrftoken': self.csrftoken,
                'filter': filter,
            }
