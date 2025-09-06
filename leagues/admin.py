from django.contrib import admin
from .models import League


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """
    Admin configuration for the League model.
    """

    list_display = (
        "id",
        "title",
        "created_by",
        "habit",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("start_date", "end_date", "created_by")
    search_fields = ("title", "description", "rules", "rewards", "created_by__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("title", "description", "image", "habit", "created_by"),
            },
        ),
        (
            "Participation",
            {
                "fields": ("participants",),
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    "start_date",
                    "end_date",
                ),
            },
        ),
        (
            "Additional Details",
            {
                "fields": ("rules", "rewards"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
            },
        ),
    )
