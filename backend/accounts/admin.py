"""L'admin Django par défaut suffit pour User. Pas de modèle custom ici."""

from django.contrib import admin

from .models import DataRequest


@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "request_type", "status", "created_at", "responded_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "notes")
    readonly_fields = ("created_at", "responded_at")
    ordering = ("-created_at",)
