from django.contrib import admin

from .models import Comment, Post, UserProfile


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at", "updated_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
