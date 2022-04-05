from . import views
from .compat import patterns, url

urlpatterns = patterns(url(r"^(?P<name>.+)/$", views.viewlet_view, name="viewlet"))
