from django.urls import path

from . import views

app_name = "exam"
urlpatterns = [
    path("", views.index, name="index"),
    path("exam/", views.exam, name="exam"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote")
]