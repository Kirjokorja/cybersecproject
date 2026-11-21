from django.db import migrations
# from django.contrib.auth.models import User
from exam.models import User, Choice, Question, Exam, Result, EventGroup, LogEvent, EventSeverity

def add_event_severity_level(apps, schema_editor):
    EventSeverity.objects.create(severity_name="info", severity_level=1)
    EventSeverity.objects.create(severity_name="warning", severity_level=2)
    EventSeverity.objects.create(severity_name="error", severity_level=3)
    EventSeverity.objects.create(severity_name="critical", severity_level=4)

def add_event_groups(apps, schema_editor):
    level_2 = EventSeverity.objects.get(severity_level=2)
    level_3 = EventSeverity.objects.get(severity_level=3)

    EventGroup.objects.create(group_name="User Actions", severity_level=level_2)
    EventGroup.objects.create(group_name="Admin Actions", severity_level=level_3)

def add_log_events(apps, schema_editor):
    level_3 = EventSeverity.objects.get(severity_level=3)
    level_4 = EventSeverity.objects.get(severity_level=4)
    user_actions = EventGroup.objects.get(group_name="User Actions")
    admin_actions = EventGroup.objects.get(group_name="Admin Actions")

    LogEvent.objects.create(event_group=user_actions, event_name="register user success", severity_level=user_actions.severity_level)
    LogEvent.objects.create(event_group=user_actions, event_name="register user failed", severity_level=user_actions.severity_level)
    LogEvent.objects.create(event_group=user_actions, event_name="login success", severity_level=user_actions.severity_level)
    LogEvent.objects.create(event_group=user_actions, event_name="login failed", severity_level=user_actions.severity_level)
    LogEvent.objects.create(event_group=user_actions, event_name="locked account login attempt", severity_level=level_3)
    LogEvent.objects.create(event_group=user_actions, event_name="consecutive failed login attempts", severity_level=level_3)
    LogEvent.objects.create(event_group=user_actions, event_name="logout", severity_level=user_actions.severity_level)

    LogEvent.objects.create(event_group=admin_actions, event_name="admin register success", severity_level=admin_actions.severity_level)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin register failed", severity_level=admin_actions.severity_level)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin login success", severity_level=admin_actions.severity_level)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin login failed", severity_level=admin_actions.severity_level)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin login attempt to normal user pages", severity_level=level_3)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin locked account login attempt", severity_level=level_3)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin consecutive failed login attempts", severity_level=level_4)
    LogEvent.objects.create(event_group=admin_actions, event_name="admin logout", severity_level=admin_actions.severity_level)
    

def add_users(apps, schema_editor):
    User.objects.create_superuser(username="admin", email="admin@example.com", password="thesuperboss")
    User.objects.create_user(username="seppo", password="smithingismylife")
    User.objects.create_user(username="onerva", password="letsplayhayday")

def add_questions(apps, schema_editor):
    withers = Choice.objects.create(choice_text="withers")
    q= Question.objects.create(question_text="What is the highest point of a horse's back called?", answer=withers)
    croup = q.choices.create(choice_text="croup")
    q.choices.create(choice_text="fetlock")
    muzzle = q.choices.create(choice_text="muzzle")
    poll = q.choices.create(choice_text="poll")

    pastern = Choice.objects.create(choice_text="pastern")
    q = Question.objects.create(question_text="What is the part of a horse's leg called that connects the hoof and the fetlock?", answer=pastern)
    q.choices.add(croup)
    q.choices.add(muzzle)
    q.choices.add(poll)
    q.choices.create(choice_text="ergot")

    answer_1 = Choice.objects.create(choice_text="answer 1")
    q = Question.objects.create(question_text="Test Question 1", answer=answer_1)
    q.choices.create(choice_text="test choice 1")
    q.choices.create(choice_text="test choice 2")
    q.choices.create(choice_text="test choice 3")
    q.choices.create(choice_text="test choice 4")

    answer_2 = Choice.objects.create(choice_text="answer 2")
    q = Question.objects.create(question_text="Test Question 2", answer=answer_2)
    q.choices.create(choice_text="test choice 5")
    q.choices.create(choice_text="test choice 6")
    q.choices.create(choice_text="test choice 7")
    q.choices.create(choice_text="test choice 8")

def add_exams(apps, schema_editor):
    exam_equine = Exam.objects.create(name="Equine Anatomy")
    exam_test = Exam.objects.create(name="Test Exam 1")

    questions_equine = Question.objects.filter(id__lt=3)
    questions_test = Question.objects.filter(question_text__contains="Test")

    for q in questions_equine:
        exam_equine.questions.add(q)
    exam_equine.save()

    for q in questions_test:
        exam_test.questions.add(q)
    exam_test.save()

def add_participants_to_exams(apps, schema_editor):

    onerva = User.objects.get(username="onerva")
    seppo = User.objects.get(username="seppo")

    exam_equine = Exam.objects.get(name="Equine Anatomy")
    exam_test = Exam.objects.get(name="Test Exam 1")

    for q in exam_equine.questions.all():
        Result.objects.create(exam=exam_equine, question=q, participant=onerva)
        Result.objects.create(exam=exam_equine, question=q, participant=seppo)

    for q in exam_test.questions.all():
        Result.objects.create(exam=exam_test, question=q, participant=onerva)

def remove_event_severity_level(apps, schema_editor):
    EventSeverity.objects.all().delete()

def remove_event_groups(apps, schema_editor):
    EventGroup.objects.all().delete()

def remove_log_events(apps, schema_editor):
    LogEvent.objects.all().delete()

def remove_users(apps, schema_editor):
    User.objects.all().delete()

def remove_exams(apps, schema_editor):
    Exam.objects.all().delete()

def remove_questions(apps, schema_editor):
    Question.objects.all().delete()

def forward(apps, schema_editor):
    add_event_severity_level(apps, schema_editor)
    add_event_groups(apps, schema_editor)
    add_log_events(apps, schema_editor)
    add_users(apps, schema_editor)
    add_questions(apps, schema_editor)
    add_exams(apps, schema_editor)
    add_participants_to_exams(apps, schema_editor)

def reverse(apps, schema_editor):
    remove_event_severity_level(apps, schema_editor)
    remove_event_groups(apps, schema_editor)
    remove_log_events(apps, schema_editor)
    remove_users(apps, schema_editor)
    remove_exams(apps, schema_editor)
    remove_questions(apps, schema_editor)

class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
