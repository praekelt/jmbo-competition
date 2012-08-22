from django.conf.urls.defaults import patterns, url


'''url(r'^list/$', 'object_list', 
            name='competition-object-list'),'''
urlpatterns = patterns(
    'competition.views',
    url(
        r'^info/$', 
        'preferences_info',
        name='competition-preferences-info'
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        'competition_detail',
        name='competition-detail',
    ),
)
