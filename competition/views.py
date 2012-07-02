from django.utils.translation import ugettext as _
from django.contrib import messages
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from jmbo.generic.views import GenericObjectList, GenericObjectDetail

from preferences import preferences

from competition.models import Competition, CompetitionPreferences
from competition.view_modifiers import CompetitionViewModifier
from competition.forms import CompetitionEntryForm


class ObjectList(GenericObjectList):
    def get_extra_context(self, *args, **kwargs):
        return {'title': 'Competitions'}

    def get_view_modifier(self, request, *args, **kwargs):
        return CompetitionViewModifier(request=request, slug=None)

    def get_paginate_by(self, *args, **kwargs):
        return 7

    def get_queryset(self, *args, **kwargs):
        return Competition.permitted.all().order_by('start_date')

object_list = ObjectList()


class PreferencesInfo(GenericObjectDetail):
    def get_extra_context(self, *args, **kwargs):
        return {'title': 'Competitions'}

    def get_view_modifier(self, request, *args, **kwargs):
        return CompetitionViewModifier(request=request, slug=None)

    def get_queryset(self, *args, **kwargs):
        return CompetitionPreferences.objects.all()

    def get_template_name(self, *args, **kwargs):
        return 'competition/competitionpreferences_detail.html'

    def __call__(self, request, *args, **kwargs):
        self.params['object_id'] = preferences.CompetitionPreferences.id
        return super(PreferencesInfo, self).__call__(
            request,
            *args,
            **kwargs
        )

preferences_info = PreferencesInfo()


def competition_detail(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    if request.method == 'POST':
        form = CompetitionEntryForm(request.POST)
        if form.is_valid():
            form.save()
            msg = _("You have entered the competition")
            messages.success(request, msg, fail_silently=True)
    else:
        form = CompetitionEntryForm()
    
    extra = {"competition_entry_form": form, "object": competition,
        "view_modifier": CompetitionViewModifier(request=request, slug=None)}
    return render_to_response("competition/competition_detail.html", extra,
        context_instance=RequestContext(request))

