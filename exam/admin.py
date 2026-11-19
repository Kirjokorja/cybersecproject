from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Question, Choice, Exam, Result, EventEscalation, EventGroup, LogEvent, Log

class ResultsInLine(admin.TabularInline):
    model = Result

class UserAdmin(BaseUserAdmin):
    inlines = [ResultsInLine]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('login_attempts',)
        }),
    )

class LogAdmin(admin.ModelAdmin):
    list_display = ["time", "event_type", "message", "actor", "event_type__escalation_level", "event_type__event_group"]
    list_filter = ["time", "event_type", "message", "actor", "event_type__escalation_level", "event_type__event_group"]
    search_fields = ["time", "event_type", "message", "actor", "event_type__escalation_level", "event_type__event_group"]

admin.site.register(User, UserAdmin)
admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(EventEscalation)
admin.site.register(EventGroup)
admin.site.register(LogEvent)
admin.site.register(Log, LogAdmin)
