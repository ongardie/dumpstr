from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url('^.*$', 'webmetrics.views.home'),
)
