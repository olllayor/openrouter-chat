# views.py
import json
import os
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings

from chat.groq_client import get_groq_chat_completion
from .models import UserProfile, Chat, Message
from django.contrib.auth.models import User

# Import the streaming function from openrouter.py
from .openrouter_client import stream_openrouter_response


# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# This constant remains in views if needed elsewhere.
OPENROUTER_MODELS_ENDPOINT = (
    "https://openrouter.ai/api/v1/models?supported_parameters=free"
)


def index(request):
    """
    Render the chat interface.
    """
    return render(request, "chat/index.html")


def save_messages(chat, prompt, response_content, is_error=False):
    """
    Save the user prompt and the AI's response as Message objects.
    """
    Message.objects.create(chat=chat, sender="user", content=prompt)
    Message.objects.create(
        chat=chat,
        sender="ai",
        content=f"Error: {response_content}" if is_error else response_content,
    )


# @login_required
# @csrf_exempt
# def ask_chat(request):
#     # Ensure user is authenticated.
#     if not request.user.is_authenticated:
#         return JsonResponse(
#             {
#                 "error": "Please login to continue",
#                 "login_url": reverse("admin:login"),
#             },
#             status=401,
#         )

#     # Only allow POST requests.
#     if request.method != "POST":
#         return JsonResponse({"error": "Only POST allowed."}, status=405)

#     # CSRF token check for AJAX requests.
#     if not request.headers.get("X-CSRFToken") and not request.META.get("HTTP_X_CSRFTOKEN"):
#         return HttpResponseForbidden("CSRF token missing")

#     try:
#         data = json.loads(request.body)
#         prompt = data.get("prompt", "")
#         model = data.get("model", "")
#     except Exception:
#         return JsonResponse({"error": "Invalid request body."}, status=400)

#     user = request.user
#     chat_id = request.session.get("chat_id")
#     chat = (
#         Chat.objects.get(id=chat_id, user=user)
#         if chat_id
#         else Chat.objects.create(user=user, title=f"Chat with {model}")
#     )
#     request.session["chat_id"] = chat.id

#     # Determine which API key to use.
#     api_key_to_use = os.getenv("OPENROUTER_API_KEY")
#     try:
#         user_profile = UserProfile.objects.get(user=user)
#         if user_profile.api_token:
#             api_key_to_use = user_profile.api_token
#     except UserProfile.DoesNotExist:
#         pass

#     # Retrieve past messages from the chat and add the current prompt.
#     messages_history = [
#         {"role": msg.sender, "content": msg.content}
#         for msg in Message.objects.filter(chat=chat).order_by("created_at")
#     ]
#     messages_history.append({"role": "user", "content": prompt})

#     # Build the payload for the API call.
#     payload = {"model": model, "messages": messages_history, "stream": True}
#     headers = {
#         "Authorization": f"Bearer {api_key_to_use}",
#         "Content-Type": "application/json",
#         "HTTP-Referer": request.META.get("HTTP_REFERER", ""),
#         "X-Title": "Django Chat App",
#     }

#     # Define a generator for streaming the response using our separated API logic.
#     stream_generator = stream_openrouter_response(payload, headers, chat, prompt, save_messages)

#     return StreamingHttpResponse(stream_generator, content_type="text/plain")





@login_required
@csrf_exempt
def ask_groq_chat(request):
    """
    Handle chat requests using Groq API integration.
    This view builds the chat history, sanitizes the roles, appends the user's prompt, calls Groq,
    and then stores and returns the assistant's response.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    # CSRF token check for AJAX requests.
    if not request.headers.get("X-CSRFToken") and not request.META.get(
        "HTTP_X_CSRFTOKEN"
    ):
        return JsonResponse({"error": "CSRF token missing"}, status=403)

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        # Allow selecting a model, with a default value.
        model = data.get("model", "llama-3.2-11b-vision-preview")
    except Exception:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    user = request.user
    chat_id = request.session.get("chat_id")
    chat = (
        Chat.objects.get(id=chat_id, user=user)
        if chat_id
        else Chat.objects.create(user=user, title=f"Chat with Groq ({model})")
    )
    request.session["chat_id"] = chat.id

    # Build chat history from stored messages (ordered by creation time).
    raw_chat_history = [
        {"role": msg.sender, "content": msg.content}
        for msg in Message.objects.filter(chat=chat).order_by("created_at")
    ]

    # Map roles to valid values for Groq API.
    valid_roles = {"system", "user", "assistant"}
    sanitized_history = []
    for message in raw_chat_history:
        role = message.get("role")
        # Convert 'ai' to 'assistant'
        if role == "ai":
            role = "assistant"
        # If role is not valid, default to 'assistant'
        if role not in valid_roles:
            role = "assistant"
        sanitized_history.append({"role": role, "content": message.get("content")})

    # Append the new user prompt to the sanitized chat history.
    sanitized_history.append({"role": "user", "content": prompt})

    # Get the assistant's reply from Groq API.
    assistant_reply = get_groq_chat_completion(sanitized_history, model=model)

    # Save the user prompt and the assistant's reply in the database.
    Message.objects.create(chat=chat, sender="user", content=prompt)
    Message.objects.create(chat=chat, sender="assistant", content=assistant_reply)

    # Return the assistant's reply as JSON.
    return JsonResponse({"response": assistant_reply})
