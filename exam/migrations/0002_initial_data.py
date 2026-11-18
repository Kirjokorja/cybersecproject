from django.db import migrations
# from django.contrib.auth.models import User
from exam.models import User, Choice, Question, Exam, Result

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

def remove_users(apps, schema_editor):
    User.objects.all().delete()

def remove_exams(apps, schema_editor):
    Exam.objects.all().delete()

def remove_questions(apps, schema_editor):
    Question.objects.all().delete()

def forward(apps, schema_editor):
    add_users(apps, schema_editor)
    add_questions(apps, schema_editor)
    add_exams(apps, schema_editor)
    add_participants_to_exams(apps, schema_editor)

def reverse(apps, schema_editor):
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
