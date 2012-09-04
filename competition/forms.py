from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import fromstr, LineString

from django.core.urlresolvers import reverse

from jmbo.forms import as_div

from competition.models import CompetitionEntry


class CompetitionBaseEntryForm(forms.Form):
    accept_terms = forms.BooleanField(
        required=True,
        label="",
    )
    location = forms.CharField(
        widget=forms.HiddenInput,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.competition = kwargs.pop('competition')
        super(CompetitionBaseEntryForm, self).__init__(*args, **kwargs)
        # put accept_terms checkbox after all other fields
        self.fields.keyOrder.remove('accept_terms')
        self.fields.keyOrder.append('accept_terms')
        if not self.competition.check_in_distance:
            del self.fields['location']

    def clean(self):
        if not self.competition.can_enter(self.request):
            raise forms.ValidationError(_("You are not allowed to enter this competition."))
        return super(CompetitionBaseEntryForm, self).clean()
    
    def clean_location(self):
        p = fromstr(self.cleaned_data['location'])
        line = LineString(p, self.competition.location.coordinates, srid=4326)
        line.transform(53031)
        if line.length > self.competition.check_in_distance:
            raise forms.ValidationError(_("""You are not close enough to 
                enter the competition, or you GPS might not be turned on. In the latter 
                case, turn on your device's GPS and reload the page."""))
        return self.cleaned_data['location']

    def save(self):
        entry = CompetitionEntry(
            user=self.request.user,
            competition=self.competition,
        )
        entry.save()

    as_div = as_div


class SingleAnswerEntryForm(CompetitionBaseEntryForm):
    answer = forms.CharField(
        max_length=255,
        required=True
    )

    def save(self):
        entry = CompetitionEntry(
            user=self.request.user,
            competition=self.competition,
            answer_text=self.cleaned_data['answer']
        )
        entry.save()


class MultichoiceEntryForm(CompetitionBaseEntryForm):
    option = forms.ChoiceField(
        widget=RadioSelect,
        choices=[],
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(MultichoiceEntryForm, self).__init__(*args, **kwargs)
        self.fields['option'].choices = \
            [(o.id, o.text) for o in self.competition.competitionansweroption_set.all()]

    def save(self):
        entry = CompetitionEntry(
            user=self.request.user,
            competition=self.competition,
            answer_option_id=self.cleaned_data['option']
        )
        entry.save()


class FileUploadEntryForm(CompetitionBaseEntryForm):
    file = forms.FileField(
        required=True
    )

    def clean_file(self):
        if self.cleaned_data['file'].size > self.competition.max_file_size * 1024:
            raise forms.ValidationError(_("The file is too large. It may not be larger than %d kB." \
                % self.competition.max_file_size))
        return self.cleaned_data['file']

    def save(self):
        entry = CompetitionEntry(
            user=self.request.user,
            competition=self.competition,
            answer_file=self.cleaned_data['file']
        )
        entry.save()