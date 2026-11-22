from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Question, Choice, Exam, Result, EventSeverity, EventGroup, LogEvent, Log

class ResultsInLine(admin.TabularInline):
    model = Result

class UserAdmin(BaseUserAdmin):
    inlines = [ResultsInLine]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('login_attempts',)
        }),
    )

class EventSeverityAdmin(admin.ModelAdmin):
    list_display = [
            "severity_name",
            "level"
        ]
    list_filter = [
            "severity_name",
            "level"
        ]
    search_fields = [
            "severity_name",
            "level"
        ]

class EventGroupAdmin(admin.ModelAdmin):
    list_display = [
            "group_name",
            "severity_level__severity_name",
            "severity_level__level"
        ]
    list_filter = [
            "group_name",
            "severity_level__severity_name",
            "severity_level__level"
        ]
    search_fields = [
            "group_name",
            "severity_level__severity_name",
            "severity_level__level"
        ]

class LogEventAdmin(admin.ModelAdmin):
    list_display = [
            "event_group__group_name",
            "event_name",
            "severity_level__severity_name",
            "severity_level__level"
        ]
    list_filter = [
            "event_group__group_name",
            "event_name",
            "severity_level__severity_name",
            "severity_level__level"
        ]
    search_fields = [
            "event_group__group_name",
            "event_name",
            "severity_level__severity_name",
            "severity_level__level"
        ]

class LogAdmin(admin.ModelAdmin):
    list_display = [
            "id",
            "time", 
            "event_type",
            "message", 
            "actor", 
            "event_type__severity_level", 
            "event_type__event_group"
        ]
    list_filter = [
            "event_type",  
            "actor", 
            "event_type__severity_level", 
            "event_type__event_group"
        ]
    search_fields = [
            "id",
            "time", 
            "event_type", 
            "message", 
            "actor", 
            "event_type__severity_level", 
            "event_type__event_group"
        ]

admin.site.register(User, UserAdmin)
admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(EventSeverity, EventSeverityAdmin)
admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(LogEvent, LogEventAdmin)
admin.site.register(Log, LogAdmin)
