from django.db import models
from django.apps import apps
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class CustomUserManager(BaseUserManager):

    def _create_any_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        # FLAW 2: Cryptographic Failures
        # user.password = make_password(password)
        user.password = password

        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_any_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_any_user(username, email, password, **extra_fields)

class User(AbstractUser):
    login_attempts = models.IntegerField(default=0)

    objects = CustomUserManager()

    # FLAW 2: Cryptographic Failures
    def set_password(self, raw_password):
        self.password = raw_password
        # password hashing
        # self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        # password check
        # return check_password(raw_password, self.password, setter)
        if raw_password == self.password:
            return True
        return False


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
    questions = models.ManyToManyField(Question)

    def __str__(self):
            return self.name

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answered = models.IntegerField(default=-1)

    def __str__(self):
        return self.participant.username + "_" + self.exam.name + "_" + self.question.question_text

class EventEscalation(models.Model):
    escal_name = models.CharField(unique=True)
    escal_level = models.IntegerField(unique=True)

    def __str__(self):
        return self.escalation_name + "_" + str(self.escalation_level)

class EventGroup(models.Model):
    group_name = models.CharField(unique=True)
    escalation_level = models.ForeignKey(EventEscalation, on_delete=models.CASCADE)

    def __str__(self):
        return self.group_name

class LogEvent(models.Model):
    event_group = models.ForeignKey(EventGroup, on_delete=models.CASCADE)
    event_name = models.CharField()
    escalation_level = models.ForeignKey(EventEscalation, on_delete=models.CASCADE)

    def __str__(self):
        return self.event_group + "_" + self.event_name

class Log(models.Model):
    time = models.DateTimeField(auto_now=True)
    event_type = models.ForeignKey(LogEvent, null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.time) + "_" + self.event_type
