from django.contrib import admin
from .models import UserProfile, Chat, Message

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_limit', 'tokens_used', 'api_token')
    search_fields = ('user__username',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'title')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'created_at', 'tokens_consumed')
    list_filter = ('sender', 'created_at')
    search_fields = ('chat__title', 'content')
