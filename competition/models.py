import os

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from jmbo.models import ModelBase

from preferences.models import Preferences

from ckeditor.fields import RichTextField


# This model tries to encapsulate the most common forms a competition can take
class Competition(ModelBase):
    content = RichTextField(
        help_text="Background info and explanation of the competition."
    )
    check_in_distance = models.PositiveIntegerField(
        default=0,
        help_text="Distance threshold for check ins, in metres. 0 to disable checking in to enter.",
        blank=True,
        null=True,
    )
    question = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="Short competition question",
    )
    question_blurb = RichTextField(
        blank=True,
        null=True,
        help_text="Descriptive text elaborating on the question."
    )
    answer_type = models.CharField(
        max_length=32,
        choices=(
            ('free_text_input', 'Free text input'),
            ('multiple_choice_selection', 'Multiple choice selection'),
            ('file_upload', 'File upload')
        ),
        blank=True,
        null=True,
        help_text="What type of answer is expected of the user, if any?",
    )
    correct_answer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Answer used to determine winning entries. If there are multiple correct answers, enter a comma-separated list. <b>(only for answer type 'Free text input')</b>"
    )
    max_file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The maximum size in kB for a file upload.  <b>(only for answer type 'File upload')</b>"
    )
    rules = RichTextField(
        blank=True,
        null=True,
        help_text="Rules specific to this competition.",
    )
    start_date = models.DateField(
        help_text="Date the competition starts."
    )
    end_date = models.DateField(
        help_text="Date the competition ends."
    )
    max_entries_per_user = models.IntegerField(
        default=1,
        help_text="Maximum number of times a user can enter the competition.",
    )

    class Meta:
        ordering = ['end_date', 'start_date']

    def __init__(self, *args, **kwargs):
        super(Competition, self).__init__(*args, **kwargs)
        # split list of correct answers and remove leading/trailing spaces
        if self.correct_answer:
            self.correct_answer_list = [a.strip() for a in self.correct_answer.split(",")]

    def get_absolute_url(self):
        return reverse('competition-detail', kwargs={'slug': self.slug})

    def can_enter(self, request):
        if request.user.is_authenticated():
            current_date = timezone.now().date()
            if current_date < self.start_date:
                return False, 'not_started'
            elif current_date > self.end_date:
                return False, 'ended'
            else:
                if CompetitionEntry.objects.filter(user=request.user, \
                    competition=self).count() >= self.max_entries_per_user:
                    return False, 'max_entries'
                else:
                    return True, 'can_enter'
        else:
            return False, 'auth_required'

    def __unicode__(self):
        return self.title


# An option in a multichoice answer set
class CompetitionAnswerOption(models.Model):
    text = models.CharField(
        max_length=255,
        help_text="The option text shown to the user. <b>(only for answer type 'Multiple choice selection')</b>"
    )
    competition = models.ForeignKey(
        Competition
    )
    is_correct_answer = models.BooleanField(
        default=False,
        help_text="Is this option the correct answer?"
    )
    
    def __unicode__(self):
        return self.text


def get_file_upload_path(instance, filename):        
    return "competition/%s/%d%s" % (instance.competition.slug, \
        instance.user.id, os.path.splitext(filename)[1])

class CompetitionEntry(models.Model):
    competition = models.ForeignKey(
        Competition,
        related_name="competition_entries"
    )
    user = models.ForeignKey(
        User,
        related_name="competition_entries_users"
    )
    answer_text = models.CharField(
        max_length=255,
        null=True,
        blank=True 
    )
    answer_option = models.ForeignKey(
        CompetitionAnswerOption,
        null=True,
        blank=True
    )
    answer_file = models.FileField(
        upload_to=get_file_upload_path,
        null=True,
        blank=True
    )
    winner = models.BooleanField(
        help_text="Mark this competition entry as a winning entry."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Competition entry"
        verbose_name_plural = "Competition entries"

    def has_correct_answer(self):
        if self.competition.answer_type and self.competition.answer_type != 'file_upload':
            if self.competition.answer_type == 'free_text_input':
                if self.competition.correct_answer:
                    a = self.answer_text.lower() if self.answer_text else ''
                    for answer in self.competition.correct_answer_list:
                        if a == answer.lower():
                            return True
                    return False
                return True
            else:
                return self.answer_option.is_correct_answer
        return True  # unless an answer is explicitly wrong, don't return False
    has_correct_answer.short_description = "Correct/valid entry"

    def __unicode__(self):
        if self.competition.answer_type:
            if self.competition.answer_type != 'file_upload':
                return "Entry %d answered '%s'" % (self.id,
                    self.answer_text if self.answer_text else self.answer_option)
            else:
                return "Entry %d uploaded a file" % (self.id, )
        else:
            return "Entry %d" % self.id


class CompetitionPreferences(Preferences):
    __module__ = "preferences.models"

    rules = RichTextField(
        blank=True,
        null=True,
        help_text="General rules which apply to all competitions."
    )

    class Meta:
        verbose_name = "Competition preferences"
        verbose_name_plural = "Competition preferences"
