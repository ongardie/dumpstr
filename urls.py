from django.conf.urls.defaults import patterns, include, url
import settings

urlpatterns = []

if settings.DEBUG and hasattr(settings, 'STATIC_DOC_ROOT'):
    urlpatterns += patterns('',
        url(settings.STATIC_URL[1:] + r'(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT,
             'show_indexes': True})
    )

urlpatterns += patterns('',
    url('^.*$', 'webmetrics.views.home'),
)
