from snippetscream.csv_serializer import UnicodeWriter

from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import BooleanFieldListFilter
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns

from preferences.admin import PreferencesAdmin

from jmbo.admin import ModelBaseAdmin, ModelBaseAdminForm
from foundry.models import Member

from competition.models import Competition, CompetitionEntry, \
        CompetitionPreferences, CompetitionAnswerOption


class CompetitionAnswerOptionAdminFormSet(BaseInlineFormSet):
    
    def clean(self):
        cleaned_data = super(CompetitionAnswerOptionAdminFormSet, self).clean()
        if any(self.errors):
            return
        if self.instance:
            has_options = False
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data['DELETE']:
                    has_options = True
                    break
            if has_options:
                # check that answer type is multichoice if there are answer options
                if self.instance.answer_type != 'multiple_choice_selection':
                    raise forms.ValidationError(_("If you want to specify multiple choice answers, you need to set the answer type to 'Multiple choice selection'."))
                # check that there is a question if answers are specified
                if not self.instance.question:
                    raise forms.ValidationError(_("You cannot have answers without a question."))
                # check that not both multichoice and a correct free text answer are specified
                if self.instance.correct_answer:
                    raise forms.ValidationError(_("You cannot provide both a correct free text answer and answer options. Only provide answers relevant to the selected answer type."))
            else:
                # multichoice requires answer options to be set
                if self.instance.answer_type == 'multiple_choice_selection':
                    raise forms.ValidationError(_("The answer type is set to 'Multiple choice selection' but there are no answer options."))
        return cleaned_data
    

class CompetitionAdminForm(ModelBaseAdminForm):

    def clean(self):
        cleaned_data = super(CompetitionAdminForm, self).clean()
        at = cleaned_data['answer_type']
        # check that file upload had max file size set
        if at == 'file_upload' and not cleaned_data['max_file_size']:
            raise forms.ValidationError(_("You need to specify a maximum file size."))
        if at == 'free_text_input' or at == 'multiple_choice_selection':
            # check that there is a question if an answer is required
            if not cleaned_data['question']:
                raise forms.ValidationError(_("You cannot have an answer without a question."))
            # check that answer types match up
            if cleaned_data['correct_answer'] and at == 'multiple_choice_selection':
                raise forms.ValidationError(_("You specified a correct free text answer, but the answer type is not set to 'Free text input'."))
        # check that an answer type has been specified if there is a question
        if not at and cleaned_data['question']:
            raise forms.ValidationError(_("You need to specify an answer type for the question."))
        if cleaned_data['check_in_distance'] and not cleaned_data['location']:
            raise forms.ValidationError(_("You need to specify a location for the competition that can be used for check ins."));
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
            'fields': ('question', 'question_blurb', 'answer_type', 'correct_answer', 'max_file_size'),
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


# mark a competition entry as a winner
def mark_winner(modeladmin, request, queryset):
    queryset.update(winner=True)
mark_winner.short_description = "Mark selected entries as winners"

class CompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user_link', 'user_fullname',
            'user_email', 'user_cellnumber', 'has_correct_answer',
            'file_link', 'winner')
    list_filter = ('competition', 'winner')
    actions = [mark_winner]

    def user_link(self, obj):
        return '<a href="%s">%s</a>' % (reverse('admin:foundry_member_change', args=(obj.user.id, )), obj.user.__unicode__())
    user_link.allow_tags = True

    def user_fullname(self, obj):
        return obj.user.get_full_name()

    def user_email(self, obj):
        return obj.user.email

    def user_cellnumber(self, obj):
        try:
            member = Member.objects.get(pk=obj.user.pk)
            return member.mobile_number
        except Member.DoesNotExist:
            return 'Unknown'
    
    def file_link(self, obj):
        if obj.competition.answer_type == 'file_upload':
            return '<a href="%s">Download file</a>' % (obj.answer_file.url, )
        return ''
    file_link.allow_tags = True

    def get_urls(self):
        """ Extend the admin urls for the CompetitionEntryAdmin model
            to be able to invoke a CSV export view  on the admin model """
        urls = super(CompetitionEntryAdmin, self).get_urls()
        csv_urls = patterns('',
            (r'^exportcsv/$', self.admin_site.admin_view(self.csv_export))
        )
        return csv_urls + urls

    def csv_export(self, request):
        """ Return a CSV document of the competition entry and its user
            details
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=competitionentries.csv'

        # create the csv writer with the response as the output file
        writer = UnicodeWriter(response)
        writer.writerow([
            'First Name', 'Last Name', 'Email Address', 'Cell Number',
            'Question', 'Answer File', 'Answer Option', 'Answer Text',
            'Has Correct Answer', 'Winner', 'Time Stamp'
            ])
        for entry in self.queryset(request):
            writer.writerow([
                entry.user.first_name, entry.user.last_name,
                entry.user.email, 
                "%s" % self.user_cellnumber(entry),
                "%s" % entry.competition.question, 
                "%s" % entry.answer_file.name, 
                "%s" % entry.answer_option.text,
                "%s" % entry.answer_text, 
                "%s" % entry.has_correct_answer(),
                "%s" % entry.winner,
                "%s" % entry.timestamp
                ])

        return response


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(CompetitionEntry, CompetitionEntryAdmin)
admin.site.register(CompetitionPreferences, PreferencesAdmin)
