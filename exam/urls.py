from django.urls import include, path
from exam.views import ExamView, RegisterUserView

from . import views

app_name = "exam"

extra_patterns = [
    path("", ExamView.as_view(), name="exam"),
    path("<int:exam_id>/", views.results, name="results"),
    path("<int:exam_id>/question/<int:question_id>/", views.question, name="question"),
    path("<int:exam_id>/results/", views.results, name="results"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("register-user/", RegisterUserView.as_view(), name="register-user"),
    path("exam/", include(extra_patterns)),
]