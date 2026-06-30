from django.urls import path

from .views import CreateCourseView

urlpatterns = [
    path("", CreateCourseView.as_view(), name="course-create"),
]
