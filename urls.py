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

assert settings.WWW_ROOT.startswith('/')
prefix = '^%s' % settings.WWW_ROOT[1:]

urlpatterns = patterns('',
    url(prefix + r'$',
        'webmetrics.views.home'),
    url(prefix + r'report/(\d+)/?$',
        'webmetrics.views.view_report'),
    url(prefix + r'ajax/report/new/?$',
        'webmetrics.views.post_report'),
)
