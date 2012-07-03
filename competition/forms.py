from django import forms

from jmbo.forms import as_div

from competition.models import CompetitionEntry


class CompetitionEntryForm(forms.Form):
    answer = forms.CharField(max_length=255)
    
    as_div = as_div
    