"""
Endpoints /api/courses/ :
    GET  /api/courses/  — bibliothèque paginée du user connecté (T-08.1)
    POST /api/courses/  — dépôt d'un cours (PDF ou texte)
"""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from llm.pdf_utils import PDFError, extract_text_from_pdf

from .models import Course
from .serializers import (
    CourseSerializer,
    CourseSummarySerializer,
    CreateCourseSerializer,
)


class CourseView(generics.ListAPIView):
    """GET liste paginée + POST création sur /api/courses/."""

    serializer_class = CourseSummarySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        description=(
            "Liste paginée des cours de l'utilisateur connecté, triés par "
            "`created_at` décroissant. Champs : id, title, created_at."
        ),
        responses={200: CourseSummarySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=CreateCourseSerializer,
        responses={201: CourseSerializer},
        description=(
            "Dépose un cours. Fournir soit `pdf` (multipart, ≤ 5 Mo) "
            "soit `source_text` (≥ 200 caractères)."
        ),
    )
    def post(self, request):
        serializer = CreateCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data["title"]
        pdf_file = serializer.validated_data.get("pdf")
        source_text = (serializer.validated_data.get("source_text") or "").strip()

        if pdf_file:
            try:
                source_text = extract_text_from_pdf(pdf_file)
            except PDFError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        course = Course.objects.create(
            user=request.user,
            title=title,
            content=source_text,
        )
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user).order_by("-created_at")
