from django.urls import re_path

from . import views

urlpatterns = [re_path(r"^(?P<name>.+)/$", views.viewlet_view, name="viewlet")]
