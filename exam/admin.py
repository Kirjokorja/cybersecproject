from django.contrib import admin

from .models import Question, Choice, Exam, QuestionResult

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuestionResult)
admin.site.register(Exam)
