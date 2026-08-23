from django.urls import include, path

from . import views

app_name = "exam"

extra_patterns = [
    path("", views.exam, name="exam"),
    path("<int:exam_id>/question/<int:question_id>", views.question, name="question"),
    path("<int:exam_id>/results/", views.results, name="results"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("exam/", include(extra_patterns)),
]