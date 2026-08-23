from django.db.models import F
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from .models import Choice, Question, Exam

def get_exam_context(exam):
    return {"id": exam.id, "name_text": exam.name_text}

def get_exam_results(exam):
    return {"id": exam.id, "name_text": exam.name_text, "participant": exam.participant, "points": exam.points}

def get_exam_question(question):
    choices = question.choices.all().union(Choice.objects.filter(pk=question.answer.id)).order_by("choice_text")
    question_dict = {
        "id": question.id,
        "question_text": question.question_text,
        "choices": choices
    }
    return question_dict

def update_progress(exam):
    if len(exam.questions.all()) == exam.progress + 1:
        exam.progress = -1
    else:
        exam.progress += 1
    exam.save()

def update_points(exam, question, choice):
    if exam.questions.filter(id=question.id) and question.answer.id == choice.id:
        exam.points += 1
        exam.save()

@login_required
def index(request):
    exams = Exam.objects.filter(participant=request.user)
    exam_list = []
    for exam in exams:
        exam_dict = get_exam_context(exam)
        exam_list.append(exam_dict)
    return render(request, "exam/index.html", {"exam_list": exam_list})

@login_required
@require_POST
def exam(request):
    exam = get_object_or_404(Exam, pk=request.POST["exam_id"])
    if exam.participant != request.user:
        messages.warning(request, "The logged in user is not the participant of this exam.")
    else:
        if exam.questions:
            if request.POST.__contains__("question_id") and request.POST.__contains__("choice_id"):
                question = get_object_or_404(Question, pk=request.POST["question_id"])
                choice = get_object_or_404(Choice, pk=request.POST["choice_id"])
                update_points(exam, question, choice)
                update_progress(exam)
            if exam.progress == -1:
                return redirect(reverse("exam:results", kwargs={"exam_id": exam.id}))
            next_question = exam.questions.order_by("id")[exam.progress]
            return redirect(reverse("exam:question", kwargs={"exam_id": exam.id, "question_id": next_question.id}))
        messages.info(request, "The exam doesn't contain any questions.")
    return redirect(reverse("exam:index"))

# def exam(request):
#     exam = Exam.objects.get(Exam, pk=request.POST.get("exam_id"))
#     if exam.participant != request.user:
#         messages.error(request, "The logged in user is not the participant of this exam.")
#         return render(request, "exam/index.html")
#     if exam.progress > -1:
#         if exam.question_list:
#             counter = exam.progress
#             question = exam.question_list[request.POST.get(exam.progress)]
#             exam.progress += 1
#             exam.save()
#             return redirect(request, "exam/exam.html", {"exam": exam, "question": question, "counter": counter})
#         else:
#             messages.info(request, "The exam doesn't contain any questions.")
#             return render(request, "exam/index.html")
#
@login_required
@require_GET
def question(request, exam_id, question_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.participant != request.user:
        messages.warning(request, "The logged in user is not the participant of this exam.")
        return redirect(reverse("exam:index"))
    exam_dict = get_exam_context(exam)
    question = get_object_or_404(Question, pk=question_id, exam=exam_id)
    question_dict = get_exam_question(question)
    return render(request, "exam/question.html", {"exam": exam_dict, "question": question_dict})

@login_required
@require_GET
def results(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.participant != request.user:
        messages.warning(request, "The logged in user is not the participant of this exam.")
        return redirect(reverse("exam:index"))
    exam_results = get_exam_results(exam)
    return render(request, "exam/results.html", {"exam_results": exam_results})

# def register(request):
#     if request.POST:
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect("login/")
#     return render(request, reverse("exam:register"), {"form": form})
