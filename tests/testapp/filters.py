
import django_filters
from django_admin_filter.filterset import AdminFilterSet
from .models import FIELDS
from .models import ModelA


def get_filters():
    filters = dict()
    for field, data in FIELDS.items():
        filters[field] = data['filters']
    return filters


class ModelAFilter(AdminFilterSet):

    class Meta:
        model = ModelA
        fields = get_filters()
