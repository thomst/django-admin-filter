
import django_filters
from django_admin_filter.filterset import AdminFilterSet
from .models import ModelA


class ModelAFilter(AdminFilterSet):

    class Meta:
        model = ModelA
        fields = [
            'first',
            'second',
            'third',
        ]
