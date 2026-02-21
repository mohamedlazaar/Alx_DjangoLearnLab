from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "actor", "verb", "timestamp", "is_read")
    list_filter = ("is_read", "verb")
    search_fields = ("recipient__username", "actor__username", "verb")
    readonly_fields = ("timestamp",)
