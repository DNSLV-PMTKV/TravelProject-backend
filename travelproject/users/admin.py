from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from travelproject.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-id"]

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_superuser",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = ("email",)

    list_filter = ("is_active", "is_superuser")

    fieldsets = (
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        ("Booleans", {"fields": ("is_active", "is_superuser")}),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
        ("Password", {"fields": ("password",)}),
    )

    readonly_fields = ("last_login", "created_at", "updated_at")
