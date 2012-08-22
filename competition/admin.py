from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms
from django.utils.translation import ugettext_lazy as _

from preferences.admin import PreferencesAdmin

from jmbo.admin import ModelBaseAdmin, ModelBaseAdminForm

from competition.models import Competition, CompetitionEntry, \
        CompetitionPreferences, CompetitionAnswerOption


class CompetitionAnswerOptionAdminFormSet(BaseInlineFormSet):
    
    def clean(self):
        super(CompetitionAnswerOptionAdminFormSet, self).clean()
        if any(self.errors):
            return    
        if self.instance:
            has_options = False
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data['DELETE']:
                    has_options = True
                    break
            if has_options:
                if not self.instance.question:
                    raise forms.ValidationError(_("You cannot have competition answers without a question."))
                elif self.instance.correct_answer:
                    raise forms.ValidationError(_("You must either provide a correct answer or answer options, not both."))
    

class CompetitionAdminForm(ModelBaseAdminForm):

    def clean(self):
        cleaned_data = super(CompetitionAdminForm, self).clean()
        if cleaned_data['correct_answer'] and not cleaned_data['question']:
            raise forms.ValidationError(_("You cannot have competition answer without a question."))
        return cleaned_data


class CompetitionAnswerOptionAdmin(admin.StackedInline):
    model = CompetitionAnswerOption
    formset = CompetitionAnswerOptionAdminFormSet


class CompetitionAdmin(ModelBaseAdmin):
    inlines = (CompetitionAnswerOptionAdmin, )
    form = CompetitionAdminForm
    list_display = ('title', 'start_date', 'end_date', 'description', '_entries', '_get_absolute_url', '_actions')

    def __init__(self, *args, **kwargs):
        super(CompetitionAdmin, self).__init__(*args, **kwargs)
        one_liners = (('start_date', 'end_date'), )
        # magic that should go into ModelBaseAdmin at later stage
        for line in one_liners:
            for field in line:
                try:
                    fields = self.fieldsets[0][1]['fields']
                    i = fields.index(field)
                    self.fieldsets[0][1]['fields'] = fields[0:i] + \
                        fields[i + 1:]
                except:
                    continue
        self.fieldsets[0][1]['fields'] += one_liners
        
        question_fieldset = (('Competition question', {
            'fields': ('question', 'question_blurb', 'answer_type', 'correct_answer',),
            }), )
        for field in question_fieldset[0][1]['fields']:
            try:
                fields = self.fieldsets[0][1]['fields']
                i = fields.index(field)
                self.fieldsets[0][1]['fields'] = fields[0:i] + \
                    fields[i + 1:]
            except:
                continue
        self.fieldsets = self.fieldsets[0:1] + question_fieldset + self.fieldsets[1:]

    def _entries(self, obj):
        return CompetitionEntry.objects.filter(competition=obj).count()
    _entries.short_description = 'No. entries'

    
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(CompetitionEntry)
admin.site.register(CompetitionPreferences, PreferencesAdmin)
