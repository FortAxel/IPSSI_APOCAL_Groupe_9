from django.contrib import admin

from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "source", "created_at"]
    list_filter = ["user", "created_at"]
    search_fields = ["title", "content", "source"]
