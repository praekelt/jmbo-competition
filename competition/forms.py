from django import forms
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from jmbo.forms import as_div

from competition.models import CompetitionEntry


class CompetitionBaseEntryForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.competition = kwargs.pop('competition')
        super(CompetitionBaseEntryForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.competition.can_enter(self.request):
            raise forms.ValidationError(_("You are not allowed to vote on this poll."))
        return super(CompetitionBaseEntryForm, self).clean()
    
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

    def __init__(self):
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
    
    