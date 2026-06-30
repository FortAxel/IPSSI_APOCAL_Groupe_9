"""Sérialiseurs pour POST /api/courses/."""

from rest_framework import serializers

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "source_text", "created_at"]
        read_only_fields = ["id", "created_at"]


class CreateCoursePdfSerializer(serializers.Serializer):
    """Input PDF pour POST /api/courses/ (T-02.2)."""

    title = serializers.CharField(max_length=200)
    pdf = serializers.FileField()

    def validate_pdf(self, value):
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Seuls les fichiers .pdf sont acceptés.")
        return value
