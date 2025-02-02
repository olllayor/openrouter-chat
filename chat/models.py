from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Extend the built-in User model with additional fields
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # API token provided by the user (optional)
    api_token = models.CharField(max_length=255, blank=True, null=True)
    # Token limit for the user (set by admin)
    token_limit = models.IntegerField(default=1000)  # default limit (example)
    # Track tokens used so far
    tokens_used = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Profile"

# Chat model to represent a conversation
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    # You can add additional fields (e.g., last_updated)

    def __str__(self):
        return self.title if self.title else f"Chat {self.id} with {self.user.username}"

# Message model to represent each message in a chat
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=50, choices=[('user', 'User'), ('ai', 'AI')])
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    # Optionally, store the number of tokens consumed by this message.
    tokens_consumed = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.sender.capitalize()} at {self.created_at}"
