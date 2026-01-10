from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")} ),
        ("Personal info", {"fields": ("first_name", "last_name", "email")} ),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")} ),
        ("Role", {"fields": ("role", "line_manager", "phone")} ),
        ("Important dates", {"fields": ("last_login", "date_joined")} ),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "line_manager", "phone")
    list_filter = ("role", "is_staff", "is_superuser")
