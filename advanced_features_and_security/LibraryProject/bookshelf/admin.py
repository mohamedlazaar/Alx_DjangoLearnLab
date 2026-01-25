# accounts/admin.py (أو الـ app اللي عندك Book)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Book, CustomUser  # أضف CustomUser هنا

class BookAdmin(admin.ModelAdmin):
    list_filter = ('title', 'author', 'publication_year')
    search_fields = ('title', 'author')

class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "date_of_birth",
                "profile_photo",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )
    
    search_fields = ("username", "email")
    ordering = ("username",)

admin.site.register(Book, BookAdmin)

CustomUser = get_user_model()
admin.site.register(CustomUser, CustomUserAdmin)
