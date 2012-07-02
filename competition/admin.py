from django.contrib import admin

from preferences.admin import PreferencesAdmin

from jmbo.admin import ModelBaseAdmin

from competition.models import Competition, CompetitionEntry, \
        CompetitionPreferences

admin.site.register(Competition, ModelBaseAdmin)
admin.site.register(CompetitionEntry)
admin.site.register(CompetitionPreferences, PreferencesAdmin)
