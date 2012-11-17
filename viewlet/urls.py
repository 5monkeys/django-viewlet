from django.conf.urls import patterns, url


urlpatterns = patterns('viewlet.views', url(r'^(?P<name>.+)/$', 'viewlet_view', name='viewlet'))
