from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Plan, Habit


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "plan", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "plan")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password", "plan")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "title",
                    "company",
                    "country",
                    "city",
                    "bio",
                    "timezone",
                    "email_verified",
                )
            },
        ),
        ("Contact Info", {"fields": ("country_code", "phone_number")}),
        (
            "Links",
            {
                "fields": (
                    "website_url",
                    "linkedin_url",
                    "twitter_url",
                    "github_url",
                )
            },
        ),
        ("Habits", {"fields": ("habits",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "plan",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    ordering = ("email",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "features",
        "price_monthly",
        "price_annually",
        "max_habits",
        "max_leagues",
    )
    search_fields = ("name",)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


admin.site.register(CustomUser, CustomUserAdmin)
