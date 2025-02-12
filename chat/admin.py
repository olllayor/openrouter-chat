# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Chat, Message, MessageImage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "token_limit", "tokens_used", "api_token")
    search_fields = ("user__username",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username", "title")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("chat", "sender", "created_at", "tokens_consumed")
    list_filter = ("sender", "created_at")
    search_fields = ("chat__title", "content")


@admin.register(MessageImage)
class MessageImageAdmin(admin.ModelAdmin):
    list_display = ("message", "image_thumbnail")

    def image_thumbnail(self, obj):
        """
        Returns an HTML image tag for the uploaded image to display a thumbnail in the admin list view.
        """
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "-"

    image_thumbnail.short_description = "Image Preview"
