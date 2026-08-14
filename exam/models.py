from django.db import models
from django.utils import timezone
from django.contrib.auth.models import UserManager
from django.contrib.auth.base_user import AbstractBaseUser

class StudentManager(UserManager):
    def create_user(self, points=-1):
        return self.model(points=points)

class Student(AbstractBaseUser):
    points = models.IntegerField()
    manager = StudentManager()

class Choice(models.Model):
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    answer = models.OneToOneField(Choice, null=True, on_delete=models.PROTECT)
    choices = models.ManyToManyField(Choice, related_query_name="questions")

    def __str__(self):
        return self.question_text
