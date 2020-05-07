from django.core.exceptions import ImproperlyConfigured
from django_filters.filterset import FilterSetMetaclass
from django_filters.filterset import BaseFilterSet




class AdminFilterSetMetaclass(FilterSetMetaclass):
    """
    Add registry-functionalities to the FilterSetMetaclass.
    """
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if new_class._meta.model:
            new_class._REGISTRY[new_class._meta.model] = new_class
        return new_class


class AdminFilterSet(BaseFilterSet, metaclass=AdminFilterSetMetaclass):
    _REGISTRY = dict()

    @classmethod
    def by_model(cls, model):
        """
        Return the filterset for a given model.
        """
        try:
            return cls._REGISTRY[model]
        except KeyError:
            msg = "No filterset was declared for model '{}'"
            raise ImproperlyConfigured(msg.format(model.__name__))
