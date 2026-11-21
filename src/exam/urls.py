from django.urls import include, path
from exam.views import ExamView, RegisterUserView, LoginView

from . import views

app_name = "exam"

# FLAW 1: Broken Access Control
# extra_patterns = [
#     path("", ExamView.as_view(), name="exam"),
#     path("<int:exam_id>/", views.results, name="results"),
#     path("<int:exam_id>/question/<int:question_id>/", views.question, name="question"),
#     path("<int:exam_id>/results/", views.results, name="results"),
# ]

extra_patterns = [
    path("", ExamView.as_view(), name="exam"),
    path("<int:exam_id>/question/<int:question_id>/", views.question_view, name="question"),
    path("<int:exam_id>/results/<str:participant>/", views.results_view, name="results_view"),
]

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.index, name="index"),
    path("admin/exams/", views.admin_exams, name="admin-exams"),
    path("register-user/", RegisterUserView.as_view(), name="register-user"),
    path("exam/", include(extra_patterns)),
]
