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
from django.contrib.auth import authenticate, login, logout
from django.db import connection
# from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Choice, Question, Exam, Result
from .forms import RegistrationForm

logger = logging.getLogger("django")

def get_exam_context(exam):
    return {"id": exam.id, "name": exam.name}

def get_exam_context_list(exam):
    return {"id": exam[0], "name": exam[1]}

def count_points(results):
    points = 0
    for result in results:
        points += result.answered
    return points

def get_exam_question_answers(results):
    result_list = []
    for result in results:
        result_list.append({"text": result.question, "answer": result.answered})
    return result_list

def get_exam_question(question):
    choices = question.choices.all().union(Choice.objects.filter(pk=question.answer.id)).order_by("choice_text")
    question_dict = {
        "id": question.id,
        "question_text": question.question_text,
        "choices": choices
    }
    return question_dict

def update_result(result, choice):
    if result.question.answer.id == choice.id:
        result.answered = 1
    else:
        result.answered = 0
    result.save()

@login_required
@require_GET
def admin_exams(request):
    exams = Exam.objects.all()
    exam_list = []
    for exam in exams:
        exam_dict = get_exam_context(exam)
        exam_list.append(exam_dict)
    return render(request, "exam/index.html", {"exam_list": exam_list})

@login_required
@require_GET
def index(request):
    exams = None
    query = "%%"
    if request.GET.__contains__("query"):
        query = "%" + request.GET["query"] + "%"
    sql = """SELECT DISTINCT exam_exam.id,
                            exam_exam.name 
                    FROM exam_exam, exam_result 
                    WHERE exam_result.participant_id = """ + str(request.user.id) + """ 
                    AND exam_exam.id = exam_result.exam_id 
                    AND exam_exam.name LIKE '""" + query + """'
            """
    # FLAW 3: Injection
    # sql = """SELECT DISTINCT exam_exam.id,
    #                         exam_exam.name 
    #                 FROM exam_exam, exam_result 
    #                 WHERE exam_result.participant_id = %s 
    #                 AND exam_exam.id = exam_result.exam_id 
    #                 AND exam_exam.name LIKE %s
    #         """
    with connection.cursor() as cursor:
        exams = cursor.execute(sql).fetchall()
        # exams = cursor.execute(sql, [request.user.id, query]).fetchall()
    exam_list = []
    for exam in exams:
        exam_dict = get_exam_context_list(exam)
        exam_list.append(exam_dict)
    return render(request, "exam/index.html", {"exam_list": exam_list})

@method_decorator(login_required, name="dispatch")
class ExamView(View):

    def get(self, request):
        return redirect(reverse("exam:index"))

    def post(self, request):
        results = Result.objects.filter(exam=request.POST["exam_id"], participant=request.user)
        if results:
            progress = results.filter(answered = -1)
            if not progress:
                return redirect(reverse("exam:results", kwargs={"exam_id": request.POST["exam_id"]}))
            if request.POST.__contains__("question_id") and request.POST.__contains__("choice_id"):
                try:
                    result =  progress.get(exam=request.POST["exam_id"], question=request.POST["question_id"])
                except ObjectDoesNotExist:
                    logger.error(f"Question with id {request.POST["question_id"]} does not exist in results of exam {request.POST["exam_id"]} for participant {request.user} or it has already been answered.")
                    return redirect(reverse("exam:index"))
                try:
                    choice = Choice.objects.get(pk=request.POST["choice_id"])
                except ObjectDoesNotExist:
                    logger.error(f"Choice with id {request.POST["choice_id"]} does not exist.")
                    return redirect(reverse("exam:index"))
                update_result(result, choice)
                progress = results.filter(answered = -1)
                if not progress:
                    return redirect(reverse("exam:results", kwargs={"exam_id": request.POST["exam_id"]}))
            next_question = progress[0].question
            return redirect(reverse("exam:question", kwargs={"exam_id": request.POST["exam_id"], "question_id": next_question.id}))
        logger.info(f"Exam {request.POST["exam_id"]} doesn't contain any results for participant {request.user}.")
        return redirect(reverse("exam:index"))

@login_required
@require_GET
def question(request, exam_id, question_id):
    try:
        result = Result.objects.get(exam=exam_id, participant=request.user, question=question_id)
    except ObjectDoesNotExist:
        logger.error(f"Question {question_id} does not exist in results of exam {exam_id} for participant {request.user} or it has already been answered.")
        return redirect(reverse("exam:index"))
    exam_dict = get_exam_context(result.exam)
    if result.answered == -1:
        question_dict = get_exam_question(result.question)
        return render(request, "exam/question.html", {"exam": exam_dict, "question": question_dict})
    logger.error(f"Question {question_id} in results of exam {exam_id} for participant {request.user} has already been answered.")
    messages.info(request, "The question has already been answered.")
    return redirect(reverse("exam:index"))

@login_required
@require_GET
def results(request, exam_id):
    results = Result.objects.filter(exam=exam_id, participant=request.user)
    if results:
        progress = results.filter(answered = -1)
        if progress:
            logger.info(f"Exam {exam_id} has not been taken yet by {request.user}.")
            messages.info(request, "The exam has not been taken yet.")
            return redirect(reverse("exam:index"))
        question_list = get_exam_question_answers(results)
        context = {"exam_id": exam_id, "exam_name": results[0].exam.name, "participant": results[0].participant.username, "questions": question_list, "points": count_points(results)}
        return render(request, "exam/results.html", context)
    logger.error(f"Exam {exam_id} does not have any results for user {request.user} or the exam does not exist.")
    return redirect(reverse("exam:index"))

@method_decorator(csrf_exempt, name="dispatch")
class RegisterUserView(View):

    def get(self, request):
        context = {}
        context['form'] = RegistrationForm()
        return render(request, "exam/register_user.html", context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # sql = "INSERT INTO auth_user (username, password, is_superuser, last_name, email, is_staff, is_active, date_joined, first_name) VALUES('" + form.data["username"] + "', '" + form.data["password1"] + "', 0, '', '', 0, 1, datetime(), '')"
            # with connection.cursor() as cursor:
            #     cursor.execute(sql)
            form.save()
            messages.info(request, "The user has been created successfuly.")
            return redirect(reverse("exam:index"))
        for error in form.errors.keys():
            logger.info(f"{error}: {form.errors[error][0]}")
            if error == "username":
                messages.info(request, f"Username: {form.errors[error][0]}")
            if error == "password1":
                        messages.info(request, f"Password 1: {form.errors[error][0]}")
            if error == "password2":
                        messages.info(request, f"Password 2: {form.errors[error][0]}")
        return redirect(reverse("exam:register-user"))

# class LoginView(View):

#     def get(self, request):
#         context = {}
#         context['form'] = AuthenticationForm()
#         return render(request, "exam/login.html", context)

    def post(self, request):
        # username = request.POST["username"]
        # password = request.POST["password"]
        # # sql = "SELECT id, password FROM auth_user WHERE username = %s"
        # # result = None
        # # with connection.cursor() as cursor:
        # #     result = cursor.execute(sql, [username]).fetchall()
        # sql = "SELECT * FROM auth_user WHERE username = %s"
        # user = User.objects.raw(sql, [username])
        # if user:
        #     # user_id = result[0][0]
        #     # user_password = result[0][1]
        #     if password == user[0].password:
        #         login(request, User.objects.get(pk=user[0].id))
        #         return redirect(reverse("exam:index"))
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse("exam:index"))
        logger.error(f"User '{request.POST["username"]}' attempted login with invalid credentials.")
        for error in form.errors.keys():
            logger.error(f"{error}: {form.errors[error][0]}")
            messages.info(request, f"{form.errors[error][0]}")
        # messages.info(request, f"Invalid credentials.")
        return redirect(reverse("exam:login"))

def logout_view(request):
    logout(request)
    return redirect(reverse("exam:index"))