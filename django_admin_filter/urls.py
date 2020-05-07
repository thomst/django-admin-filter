from django.conf.urls import re_path
from .views import FilterQueryView


urlpatterns = [
    re_path(r'^(?P<app_label>\w+)/(?P<model>\w+)/c/filter$', FilterQueryView.as_view()),
    re_path(r'^(?P<app_label>\w+)/(?P<model>\w+)/c/filter/(?P<pk>\d+)$', FilterQueryView.as_view()),
]
