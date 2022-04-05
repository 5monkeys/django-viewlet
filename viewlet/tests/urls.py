from ..compat import include, patterns, url

urlpatterns = patterns(url(r"viewlet/", include("viewlet.urls")))
