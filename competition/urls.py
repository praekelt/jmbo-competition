from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'competition.views',
    url(r'^list/$', 'object_list', 
            name='competition-object-list'),
    url(r'^info/$', 'preferences_info',
            name='competition-preferences-info'),
    url(r'^(?P<slug>[\w-]+)/$', 'object_detail',
            name='competition-object-detail',),
)
