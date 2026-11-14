from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Question, Choice, Exam, Result

class ResultsInLine(admin.TabularInline):
    model = Result

class UserAdmin(BaseUserAdmin):
    inlines = [ResultsInLine]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Result)

