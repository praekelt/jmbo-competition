from datetime import datetime, date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.contenttypes.models import ContentType

from jmbo.models import ModelBase

from preferences.models import Preferences

from ckeditor.fields import RichTextField


# This model tries to encapsulate the most common forms a competition can take
class Competition(ModelBase):
    content = RichTextField()
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
    correct_answer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Answer used to determine winning entries. If there are multiple correct answers, enter a comma-separated list (not case-sensitive). If multichoice answers are required, see answer options below."
    )
    rules = RichTextField(
        blank=True,
        null=True,
        help_text="Rules specific to this competition.",
    )
    max_entries_per_user = models.IntegerField(
        default=1
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date the competition starts."
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date the competition ends."
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
            current_date = date.today()
            if current_date < self.start_date:
                return False, 'not_started'
            elif current_date > self.end_date:
                return False, 'ended'
            else:
                if CompetitionEntry.objects.filter(user=request.user) \
                    .count() >= self.max_entries_per_user:
                    return False, 'max_entries'
                else:
                    return True, 'can_enter'
        else:
            return False, 'auth_required'

    def __unicode__(self):
        return self.title


# An option in a multichoice answer set
class CompetitionAnswerOption(models.Model):
    text = models.CharField(max_length=255)
    competition = models.ForeignKey(
        Competition
    )
    is_correct_answer = models.BooleanField(
        default=False,
        help_text="Is this option the correct answer?"
    )
    
    def __unicode__(self):
        return "%s - %s" % (self.competition.title, self.text)


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
    winner = models.BooleanField(
        help_text="Mark this competition entry as a winning entry."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Competition entry"
        verbose_name_plural = "Competition entries"

    def has_correct_answer(self):
        if self.answer_text and self.competition.correct_answer:
            for answer in self.competition.correct_answer_list:
                if self.answer_text.lower() == answer.lower():
                    return True
        elif self.answer_option:
            return self.answer_option.is_correct_answer
        return False

    def __unicode__(self):
        return "%s answered %s" % (self.user.username,
            self.answer_text if self.answer_text else self.answer_option)


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
