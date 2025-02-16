# models.py
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# Extend the built-in User model with additional fields.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    api_token = models.CharField(max_length=255, blank=True, null=True)
    token_limit = models.IntegerField(default=1000)  # default limit (example)
    tokens_used = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Profile"

    def has_enough_tokens(self, tokens_to_consume):
        """Checks if the user has enough tokens remaining."""
        return self.tokens_used + tokens_to_consume <= self.token_limit

    def consume_tokens(self, tokens):
        """Consumes tokens, raising an exception if the limit is exceeded."""
        if not self.has_enough_tokens(tokens):
            raise ValueError("Not enough tokens remaining.")
        self.tokens_used += tokens
        self.save()

    def reset_tokens(self):
        """reset tokens daily"""
        self.tokens_used = 0
        self.save()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create or update a UserProfile
    whenever a User instance is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


# Chat model to represent a conversation.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title if self.title else f"Chat {self.id} with {self.user.username}"


# Message model to represent each message in a chat.
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=50, choices=[("user", "User"), ("ai", "AI")])
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    tokens_consumed = models.IntegerField(default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.sender.capitalize()} at {self.created_at}"

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["sender"]),
        ]


# New model to store multiple images per message.
class MessageImage(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="aichat_images/")

    def __str__(self):
        return f"Image for Message {self.message.id}"

    def clean(self):
        if self.tokens_consumed < 0:
            raise ValidationError("Tokens consumed cannot be negative")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
