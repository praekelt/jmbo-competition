from django import forms

from competition.models import CompetitionEntry


class CompetitionEntryForm(forms.ModelForm):
    
    class Meta:
        model = CompetitionEntry
    