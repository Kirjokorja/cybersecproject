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
    name = models.CharField(max_length=200, default="Exam")

    def __str__(self):
            return self.name

class Results(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    answered = models.IntegerField(default=-1)

    def __str__(self):
        return self.participant.username + "_" + self.exam.name + "_" + self.question.question_text