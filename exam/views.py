import logging
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Choice, Question, Exam, QuestionResult, User
from .forms import RegistrationForm

logger = logging.getLogger("django")
logger_sec = logging.getLogger("django.security")

def get_exam_context(exam):
    return {"id": exam.id, "name_text": exam.name_text}

def count_points(results):
    points = 0
    for result in results:
        points += result.answered
    return points

def get_exam_results(exam):
    points = count_points(exam.questionresult_set.all())
    return {"id": exam.id, "name_text": exam.name_text, "participant": exam.participant, "points": points}

def get_exam_question(question):
    choices = question.choices.all().union(Choice.objects.filter(pk=question.answer.id)).order_by("choice_text")
    question_dict = {
        "id": question.id,
        "question_text": question.question_text,
        "choices": choices
    }
    return question_dict

def update_results(question_result, question, choice):
    if question.answer.id == choice.id:
        question_result.answered = 1
    else:
        question_result.answered = 0
    question_result.save()

@login_required
def index(request):
    exams = Exam.objects.filter(participant=request.user)
    exam_list = []
    for exam in exams:
        exam_dict = get_exam_context(exam)
        exam_list.append(exam_dict)
    return render(request, "exam/index.html", {"exam_list": exam_list})

@method_decorator(login_required, name="dispatch")
class ExamView(View):

    def get(self, request):
        return redirect(reverse("exam:index"))

    def post(self, request):
        try:
            exam = Exam.objects.get(pk=request.POST["exam_id"], participant=request.user)
        except ObjectDoesNotExist:
            logger_sec.warning(f"Exam can not be found with id {request.POST["exam_id"]} for participant {request.user}.")
            return redirect(reverse("exam:index"))
        if exam.progress == -1:
            return redirect(reverse("exam:results", kwargs={"exam_id": exam.id}))
        if exam.questionresult_set:
            if request.POST.__contains__("question_id") and request.POST.__contains__("choice_id"):
                try:
                    question = Question.objects.get(pk=request.POST["question_id"])
                    question_result =  exam.questionresult_set.get(question__id=question.id)
                except ObjectDoesNotExist:
                    logger.info(f"Question with id {request.POST["question_id"]} does not exist.")
                    return redirect(reverse("exam:index"))
                if question_result.answered == -1:
                    try:
                        choice = Choice.objects.get(pk=request.POST["choice_id"])
                    except ObjectDoesNotExist:
                        logger.info(f"Choice with id {request.POST["choice_id"]} does not exist.")
                        return redirect(reverse("exam:index"))
                    update_results(question_result, question, choice)
                    exam.progress += 1
                    exam.save()
                    if len(exam.questionresult_set.all()) == exam.progress:
                        exam.progress = -1
                        exam.save()
                        return redirect(reverse("exam:results", kwargs={"exam_id": exam.id}))
            next_question = exam.questionresult_set.all()[exam.progress].question
            return redirect(reverse("exam:question", kwargs={"exam_id": exam.id, "question_id": next_question.id}))
        logger.info(f"Exam {request.POST["exam_id"]} doesn't contain any questions.")
        return redirect(reverse("exam:index"))

@login_required
@require_GET
def question(request, exam_id, question_id):
    try:
        exam = Exam.objects.get(pk=exam_id, participant=request.user)
    except ObjectDoesNotExist:
        logger_sec.warning(f"Exam can not be found with id {exam_id} for participant {request.user}.")
        return redirect(reverse("exam:index"))
    exam_dict = get_exam_context(exam)
    question_result = QuestionResult.objects.get(exam__id=exam_id, question__id=question_id)
    if question_result.answered == -1:
        question_dict = get_exam_question(question_result.question)
        return render(request, "exam/question.html", {"exam": exam_dict, "question": question_dict})
    logger.info("The question has already been answered.")
    messages.info(request, "The question has already been answered.")
    return redirect(reverse("exam:index"))

@login_required
@require_GET
def results(request, exam_id):
    try:
        exam = Exam.objects.get(pk=exam_id)
    except ObjectDoesNotExist:
        logger_sec.warning(f"Exam can not be found with id {"exam_id"}.")
        return redirect(reverse("exam:index"))
    # fix for flaw 1. Broken Access Control
    # if exam.participant is not request.user:
    #     logger_sec.warning(f"The user {request.user} is not the participant of exam {exam_id}.")
    #     return redirect(reverse("exam:index"))
    if exam.progress != -1:
        logger.info("The exam has not been taken yet.")
        messages.info(request, "The exam has not been taken yet.")
        return redirect(reverse("exam:index"))
    exam_results = get_exam_results(exam)
    return render(request, "exam/results.html", {"exam_results": exam_results})

@method_decorator(csrf_exempt, name="dispatch")
class RegisterUserView(View):

    def get(self, request):
        context = {}
        context['form'] = RegistrationForm()
        return render(request, "exam/register_user.html", context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(username=form.data["username"], password=form.data["password1"])
            messages.info(request, "The user has been created successfuly.")
            return redirect(reverse("exam:index"))
        for error in form.errors.keys():
            logger.info(f"{error}: {form.errors[error][0]}")
            messages.info(request, f"{error}: {form.errors[error][0]}")
        return redirect(reverse("exam:register-user"))
