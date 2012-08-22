from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'competition.views',
    url(
        r'^(?P<slug>[\w-]+)/$',
        'competition_detail',
        name='competition-detail',
    ),
    url(
        r'^(?P<slug>[\w-]+)/terms/$',
        'competition_terms',
        name='competition-terms',
    ),
)
