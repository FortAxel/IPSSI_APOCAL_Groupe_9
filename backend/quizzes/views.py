"""
Endpoints quizz :
    GET   /api/quizzes/                — historique du user connecté
    GET   /api/quizzes/<id>/           — détail (avec les 10 questions)
    POST  /api/quizzes/<id>/answer/    — soumet 10 réponses, renvoie le score
"""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz
from .serializers import (
    QuizSerializer,
    QuizSummarySerializer,
    SubmitAnswersSerializer,
)


class QuizListView(generics.ListAPIView):
    """Historique des quizz du user connecté."""

    serializer_class = QuizSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(description="Liste paginée des quizz de l'utilisateur connecté.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizDetailView(generics.RetrieveAPIView):
    """Détail d'un quiz (les 10 questions complètes)."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user)


class AnswerQuizView(APIView):
    """Reçoit 10 réponses, calcule le score, met à jour le quiz."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SubmitAnswersSerializer,
        responses={200: OpenApiResponse(description="{ score, total, details }")},
        description=(
            "Soumet les 10 réponses et reçoit le détail de la correction. "
            "Le score est persisté sur le quiz."
        ),
    )
    def post(self, request, pk: int):
        quiz = get_object_or_404(Quiz, pk=pk, user=request.user)

        serializer = SubmitAnswersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data["answers"]

        # Index pour lookup rapide
        questions_by_idx = {q.index: q for q in quiz.questions.all()}
        if len(questions_by_idx) != 10:
            return Response(
                {"detail": "Ce quiz n'a pas 10 questions — état incohérent."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        details = []
        score = 0
        for ans in answers:
            q = questions_by_idx[ans["index"]]
            correct = (q.correct_index == ans["selected_index"])
            if correct:
                score += 1
            details.append({
                "index":          ans["index"],
                "selected_index": ans["selected_index"],
                "correct_index":  q.correct_index,
                "correct":        correct,
            })

        quiz.score = score
        quiz.save(update_fields=["score", "updated_at"])

        return Response({
            "score":   score,
            "total":   10,
            "details": details,
        })
