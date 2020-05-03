from django.conf.urls import re_path
from .views import FilterView


urlpatterns = [
    re_path(r'^(?P<app_label>\w+)/(?P<model>\w+)/c/filter$', FilterView.as_view()),
    re_path(r'^(?P<app_label>\w+)/(?P<model>\w+)/c/filter/(?P<pk>\d+)$', FilterView.as_view()),
]
