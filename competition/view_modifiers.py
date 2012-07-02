from jmbo.view_modifiers import ViewModifier
from jmbo.view_modifiers.items import URLPatternItem
from django.core.urlresolvers import reverse


class CompetitionViewModifier(ViewModifier):
    def __init__(self, request, *args, **kwargs):
        self.items = [
            URLPatternItem(
                request,
                title="Current Competitions",
                path=reverse('competition-object-list', kwargs={}),
                matching_pattern_names=['competition-object-list', ],
                default=False
            ),
            URLPatternItem(
                request,
                title="Competition Rules",
                path=reverse('competition-preferences-info', kwargs={}),
                matching_pattern_names=['competition-preferences-info', ],
                default=False
            ),
        ]
        super(CompetitionViewModifier, self).__init__(request, *args, **kwargs)
