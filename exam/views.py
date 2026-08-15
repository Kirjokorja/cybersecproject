from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Exam

@login_required
def index(request):
    latest_exam_list = Exam.objects.filter(participant=request.user)
    context = {"latest_exam_list": latest_exam_list}
    return render(request, "exam/index.html", context)

@login_required
def exam(request):
    questions = get_object_or_404(Exam, pk=request.POST.get("exam_id")).question_list.set()
    return render(request, "exam/exam.html", {"question": questions[request.POST.get("question_counter")]})

def register(request):
    if request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("login/")
    return render(request, reverse("exam:register"), {"form": form})

@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "exam/results.html", {"question": question})

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "exam/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("exam:results", args=(question.id,)))