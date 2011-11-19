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
        'dumpstr.views.home'),
    url(prefix + r'report/(\d+)/?$',
        'dumpstr.views.view_report'),
    url(prefix + r'report/latest/?$',
        'dumpstr.views.view_latest_report'),
    url(prefix + r'ajax/report/new/?$',
        'dumpstr.views.post_report'),
    url(prefix + r'ajax/description/save/?$',
        'dumpstr.views.post_description'),
    url(prefix + r'ajax/trend/([A-Za-z0-9_]+)/?$',
        'dumpstr.views.get_trend'),
)
