from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
from .models import User, Question, Choice, Exam, Result, Log

class ResultsInLine(admin.TabularInline):
    model = Result

class UserAdmin(BaseUserAdmin):
    inlines = [ResultsInLine]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('login_attempts',)
        }),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(Log)

