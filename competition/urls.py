from django.conf.urls import patterns, url


urlpatterns = patterns(
    'competition.views',
    url(
        r'^(?P<slug>[\w-]+)/$',
        'competition_detail',
        name='competition_object_detail',
    ),

    # Legacy. Must leave intact because existing customizations use it.
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
