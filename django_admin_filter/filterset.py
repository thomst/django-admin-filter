from django_filters.filterset import FilterSetMetaclass
from django_filters.filterset import BaseFilterSet


REGISTRY = dict()


class AdminFilterSetMetaclass(FilterSetMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if new_class._meta.model:
            REGISTRY[new_class._meta.model] = new_class
        return new_class


class AdminFilterSet(BaseFilterSet, metaclass=AdminFilterSetMetaclass):
    pass
