from django.urls import path

from .views import AnswerQuizView, QuizDetailView, QuizListView

urlpatterns = [
    path("",                  QuizListView.as_view(),   name="quiz-list"),
    path("<int:pk>/",         QuizDetailView.as_view(), name="quiz-detail"),
    path("<int:pk>/answer/",  AnswerQuizView.as_view(), name="quiz-answer"),
]
