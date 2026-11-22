import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from exam.models import Choice, Exam, Result, User
from exam.forms import RegistrationForm
from exam.logging.loggers import default_event_logger as event_logger

logger=logging.getLogger("django")

def get_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def reset_login_attempts(user):
    user.login_attempts = 0
    user.save()

# FLAW 5: Security Logging and Monitoring Failures
# def log_event(request, event="", actor=None, msg=""):
#     event_obj = LogEvent.objects.get(event_name=event)
#     message = msg + "."
#     if event_obj.severity_level.level > 2:
#         ip = get_ip(request)
#         message = msg + f", from IP address {ip}."
#         logger.warning(msg)
#     else:
#         logger.info(msg)
#     Log.objects.create(event_type=event_obj, message=message, actor=actor)

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

def get_exam_question(q):
    choices = q.choices.all().union(
            Choice.objects.filter(pk=q.answer.id)
        ).order_by("choice_text")
    question_dict = {
        "id": q.id,
        "question_text": q.question_text,
        "choices": choices
    }
    return question_dict

def update_result(result, choice):
    if result.question.answer.id == choice.id:
        result.answered = 1
    else:
        result.answered = 0
    result.save()

def query_exam_flawed(user_id, query):
    sql = """SELECT DISTINCT exam_exam.id,
                            exam_exam.name 
                    FROM exam_exam, exam_result 
                    WHERE exam_result.participant_id = """ + str(user_id) + """
                    AND exam_exam.id = exam_result.exam_id 
                    AND exam_exam.name LIKE '""" + query + """'
            """
    with connection.cursor() as cursor:
        exams = cursor.execute(sql).fetchall()
    return exams

def query_exam_fixed(user_id, query):
    sql = """SELECT DISTINCT exam_exam.id,
                            exam_exam.name 
                    FROM exam_exam, exam_result 
                    WHERE exam_result.participant_id = %s 
                    AND exam_exam.id = exam_result.exam_id 
                    AND exam_exam.name LIKE %s
            """
    with connection.cursor() as cursor:
        exams = cursor.execute(sql, [user_id, query]).fetchall()
    return exams

def login_data_is_valid(request, form):
    users = User.objects.filter(username=request.POST["username"])

    if users:
        user = users[0]

        if user.is_superuser:
            log_event(request=request,
                      event="admin login attempt to normal user pages",
                      actor=user,
                      msg="Admin '"+ user.username +"' attempted login to normal user pages"
            )
            return False

        if form.is_valid():
            user = form.get_user()

            if user.login_attempts > settings.MAX_LOGIN_ATTEMPTS-1:
                log_event(request=request,
                          event="locked account login attempt",
                          actor=user,
                          msg=f"User '{user.username}' attempted login to a locked account"
                )
                return False

            return True

        log_event(request=request,
            event="login failed",
            actor=user,
            msg=f"User '{request.POST["username"]}' attempted to login with invalid credentials"
        )

        if user.login_attempts > settings.MAX_LOGIN_ATTEMPTS-1:
            log_event(request=request,
                      event="locked account login attempt",
                      actor=user, msg=f"User '{user.username}' attempted login to a locked account"
            )
            return False

        if user.login_attempts == settings.MAX_LOGIN_ATTEMPTS-1:
            msg = f"""User '{user.username}' attempted to login
            with invalid credentials {settings.MAX_LOGIN_ATTEMPTS} consecutive times"""
            log_event(request=request,
                      event="consecutive failed login attempts",
                      actor=user,
                      msg=msg
            )

        user.login_attempts = user.login_attempts + 1
        user.save()
    else:
        log_event(request=request,
            event="login failed",
            msg=f"User {request.POST["username"]} attempted to login with invalid credentials"
        )

    return False

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
    exams = []
    query = "%%"

    if "query" in request.GET:
        query = "%" + request.GET["query"] + "%"

    # FLAW 3: Injection
    exams = query_exam_flawed(request.user.id, query)
    # exams = query_exam_fixed(request.user.id, query)

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
                return redirect(
                        reverse(
                            "exam:results",
                            kwargs={
                                "exam_id": request.POST["exam_id"],
                                "participant": request.user
                            }
                        )
                    )

            if "question_id" in request.POST and "choice_id" in request.POST:
                try:
                    result =  progress.get(
                        exam=request.POST["exam_id"],
                        question=request.POST["question_id"]
                    )
                except ObjectDoesNotExist:
                    logger.warning(
                        "Question with id '%s' does not exist in results of " \
                        "exam '%s' for participant '%s' or it has already been answered.", 
                        request.POST["question_id"],
                        request.POST["exam_id"],
                        request.user
                    )
                    return redirect(reverse("exam:index"))

                try:
                    choice = Choice.objects.get(pk=request.POST["choice_id"])
                except ObjectDoesNotExist:
                    logger.warning("Choice with id '%s does not exist.", request.POST["choice_id"])
                    return redirect(reverse("exam:index"))

                update_result(result, choice)
                progress = results.filter(answered = -1)

                if not progress:
                    return redirect(
                            reverse(
                                "exam:results",
                                kwargs={
                                    "exam_id": request.POST["exam_id"], 
                                    "participant": request.user
                                }
                            )
                        )

            next_question = progress[0].question
            return redirect(
                reverse(
                        "exam:question", 
                        kwargs={"exam_id": request.POST["exam_id"], "question_id": next_question.id}
                    )
                )

        logger.info("Exam %s doesn't contain any results for participant '%s'.",
                    request.POST["exam_id"], request.user)
        return redirect(reverse("exam:index"))

@login_required
@require_GET
def question_view(request, exam_id, question_id):
    try:
        result = Result.objects.get(exam=exam_id, participant=request.user, question=question_id)
    except ObjectDoesNotExist:
        logger.warning(
            "Question %s does not exist in results of exam *%s for participant '%s'.",
            question_id,
            exam_id,
            request.user
        )
        return redirect(reverse("exam:index"))

    exam_dict = get_exam_context(result.exam)

    if result.answered == -1:
        question_dict = get_exam_question(result.question)
        return render(request, "exam/question.html", {"exam": exam_dict, "question": question_dict})

    logger.info(
        "Question '%s' in results of exam '%s' for participant '%s' has already been answered.",
        question_id,
        exam_id,
        request.user
    )
    messages.info(request, "The question has already been answered.")
    return redirect(reverse("exam:index"))

@login_required
@require_GET
def results_view(request, exam_id, participant):
    results = Result.objects.filter(exam=exam_id, participant__username=participant)

    if results:
        progress = results.filter(answered = -1)

        if progress:
            logger.info("Exam '%s has not been taken yet by '%s'.", exam_id, participant)
            messages.info(request, "The exam has not been taken yet.")
            return redirect(reverse("exam:index"))

        question_list = get_exam_question_answers(results)
        context = {
            "exam_id": exam_id,
            "exam_name": results[0].exam.name,
            "participant": results[0].participant.username,
            "questions": question_list,
            "points": count_points(results)
        }
        return render(request, "exam/results.html", context)

    logger.warning(
        "Exam '%s' does not have any results for user '%s' or the exam does not exist.",
        exam_id,
        participant
    )
    return redirect(reverse("exam:index"))

# FLAW 1: Broken Access Control
# @login_required
# @require_GET
# def results_view(request, exam_id):
#     results = Result.objects.filter(exam=exam_id, participant=request.user)

#     if results:
#         progress = results.filter(answered = -1)

#         if progress:
#             logger.info(
#                 "Exam '%s' has not been taken yet by '%s'.",
#                 exam_id,
#                 request.user
#             )
#             messages.info(request, "The exam has not been taken yet.")
#             return redirect(reverse("exam:index"))

#         question_list = get_exam_question_answers(results)
#         context = {
#             "exam_id": exam_id,
#             "exam_name": results[0].exam.name,
#             "participant": results[0].participant.username,
#             "questions": question_list,
#             "points": count_points(results)
#         }
#         return render(request, "exam/results.html", context)

#     logger.warning(
#         "Exam '%s' does not have any results for user '%s' or the exam does not exist.",
#         exam_id,
#         request.user
#     )
#     return redirect(reverse("exam:index"))

@method_decorator(csrf_exempt, name="dispatch")
class RegisterUserView(View):

    def get(self, request):
        context = {}
        context['form'] = RegistrationForm()
        return render(request, "exam/register_user.html", context)

    def post(self, request):
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            user = User.objects.get(username=request.POST["username"])
            log_event(
                event="register user success",
                request=request,
                actor=user,
                msg=f"User '{user}' registered"
            )
            messages.info(request, "The user has been created successfuly.")
            return redirect(reverse("exam:index"))

        log_event(
            event="register user failed",
            request=request,
            msg=f"Attempt to register username '{request.POST["username"]}' failed"
        )
        for error in form.errors:
            logger.info("'%s': '%s'", error, form.errors[error][0])
            if error == "username":
                messages.info(request, f"Username: {form.errors[error][0]}")
            if error == "password1":
                messages.info(request, f"Password 1: {form.errors[error][0]}")
            if error == "password2":
                messages.info(request, f"Password 2: {form.errors[error][0]}")

        return redirect(reverse("exam:register-user"))

class LoginView(View):

    def get(self, request):
        context = {}
        context['form'] = AuthenticationForm()
        return render(request, "exam/login.html", context)

    def post(self, request):
        form = AuthenticationForm(data=request.POST)

        # FLAW 4: Identification and Authentication Failures
        if login_data_is_valid(request, form):
        # if form.is_valid():
            user = form.get_user()
            reset_login_attempts(user)
            login(request, user)
            log_event(
                request=request,
                event="login success",
                actor=user, msg=f"User '{user.username}' logged in"
            )
            return redirect(reverse("exam:index"))

        messages.info(request, "Invalid credentials.")
        return redirect(reverse("exam:login"))

@login_required
@require_POST
def logout_view(request):
    user = User.objects.get(pk=request.user.id)
    logout(request)
    log_event(request=request, event="logout", actor=user, msg=f"User '{user}' logged out")
    return redirect(reverse("exam:index"))
