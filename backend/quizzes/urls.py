from django.urls import path

from .views import (
    AnswerQuizView,
    GenerateQuizView,
    MistakesView,
    QuizDetailView,
    QuizListView,
    StatsView,
)

urlpatterns = [
    path("", QuizListView.as_view(), name="quiz-list"),
    path("generate/", GenerateQuizView.as_view(), name="quiz-generate"),
    # MVP2 (Lot 6) — placés AVANT <int:pk> pour ne pas être captés comme un id.
    path("stats/", StatsView.as_view(), name="quiz-stats"),
    path("mistakes/", MistakesView.as_view(), name="quiz-mistakes"),
    path("<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("<int:pk>/answer/", AnswerQuizView.as_view(), name="quiz-answer"),
]
