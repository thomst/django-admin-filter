from django.conf.urls import re_path
from .views import FilterQueryView
from .settings import URL_PATH

urlpattern = r'^(?P<app_label>\w+)/(?P<model>\w+)/{}/$'.format(URL_PATH)

urlpatterns = [
    re_path(urlpattern, FilterQueryView.as_view()),
    re_path(urlpattern + r'(?P<pk>\d+)/$', FilterQueryView.as_view()),
]
