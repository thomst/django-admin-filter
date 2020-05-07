from django.conf.urls import re_path
from .views import FilterQueryView
from . import settings


urlpatterns = [
    re_path(r'^(?P<app_label>\w+)/(?P<model>\w+)/{}$'.format(settings.URL_PATH), FilterQueryView.as_view()),
    re_path(r'^(?P<app_label>\w+)/(?P<model>\w+)/{}(?P<pk>\d+)/$'.format(settings.URL_PATH), FilterQueryView.as_view()),
]
