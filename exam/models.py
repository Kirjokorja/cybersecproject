from django.db import models
from django.contrib.auth.models import User

class Choice(models.Model):
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    answer = models.OneToOneField(Choice, on_delete=models.PROTECT)
    choices = models.ManyToManyField(Choice, related_query_name="questions")

    def __str__(self):
            return self.question_text

class Exam(models.Model):
    name_text = models.CharField(max_length=200, default="Exam")
    participant = models.OneToOneField(User, on_delete=models.CASCADE)
    question_list = models.ManyToManyField(Question)
    points = models.IntegerField()
    taken = models.BooleanField()

    def __str__(self):
        return self.name_text
