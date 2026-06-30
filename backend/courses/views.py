"""Endpoint POST /api/courses/ — dépôt d'un cours (PDF ou texte)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from llm.pdf_utils import PDFError, extract_text_from_pdf

from .models import Course
from .serializers import CourseSerializer, CreateCoursePdfSerializer


class CreateCourseView(APIView):
    """Crée un cours à partir d'un PDF (≤ 5 Mo, extraction pypdf)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=CreateCoursePdfSerializer,
        responses={201: CourseSerializer},
        description="Dépose un cours via un fichier PDF (≤ 5 Mo). Le texte est extrait et stocké.",
    )
    def post(self, request):
        serializer = CreateCoursePdfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data["title"]
        pdf_file = serializer.validated_data["pdf"]

        try:
            source_text = extract_text_from_pdf(pdf_file)
        except PDFError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        course = Course.objects.create(
            user=request.user,
            title=title,
            source_text=source_text,
        )
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)
