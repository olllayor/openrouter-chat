# views.py
import json
import os
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings

from chat.gemini_client import stream_gemini_completion
from chat.groq_client import stream_groq_chat_completion
from .models import UserProfile, Chat, Message
from django.contrib.auth.models import User

# Import the streaming function from openrouter.py
from .openrouter_client import stream_openrouter_response, OPENROUTER_MODELS_ENDPOINT


# Load environment variables
from dotenv import load_dotenv

load_dotenv()


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
# def ask_groq_chat(request):
#     """
#     Handle chat requests using Groq API integration with token streaming.
#     This view builds the chat history, sanitizes roles, appends the user's prompt,
#     streams tokens from the Groq API using the model name provided by the frontend,
#     and finally saves the assistant's complete reply to the database.
#     """
#     if request.method != "POST":
#         return JsonResponse({"error": "Only POST allowed."}, status=405)

#     # Check for CSRF token for AJAX requests.
#     if not request.headers.get("X-CSRFToken") and not request.META.get(
#         "HTTP_X_CSRFTOKEN"
#     ):
#         return JsonResponse({"error": "CSRF token missing"}, status=403)

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
#         else Chat.objects.create(user=user, title=f"Chat with Groq ({model})")
#     )
#     request.session["chat_id"] = chat.id

#     # Build raw chat history from stored messages.
#     raw_chat_history = [
#         {"role": msg.sender, "content": msg.content}
#         for msg in Message.objects.filter(chat=chat).order_by("created_at")
#     ]

#     # Sanitize roles: map 'ai' to 'assistant' and ensure valid roles.
#     valid_roles = {"system", "user", "assistant"}
#     sanitized_history = []
#     for message in raw_chat_history:
#         role = message.get("role")
#         if role == "ai":
#             role = "assistant"
#         if role not in valid_roles:
#             role = "assistant"
#         sanitized_history.append({"role": role, "content": message.get("content")})

#     # Append the new user prompt.
#     sanitized_history.append({"role": "user", "content": prompt})

#     # Create a generator for streaming tokens from Groq.
#     token_stream = stream_groq_chat_completion(sanitized_history, model=model)

#     # Save the user prompt immediately.
#     Message.objects.create(chat=chat, sender="user", content=prompt)

#     # Helper generator to stream tokens and accumulate the full reply.
#     def stream_and_save():
#         full_reply = ""
#         for token in token_stream:
#             full_reply += token
#             yield token
#         # After streaming is complete, save the assistant's full reply.
#         Message.objects.create(chat=chat, sender="assistant", content=full_reply)

#     return StreamingHttpResponse(stream_and_save(), content_type="text/plain")


@login_required
@csrf_exempt
def ask_gemini_chat(request):
    """
    Handle chat requests using Gemini API integration with token streaming.
    This view builds the chat history, appends the user's prompt,
    streams tokens from the Gemini API, and saves the assistant's complete reply.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    # Check for CSRF token for AJAX requests.
    if not request.headers.get("X-CSRFToken") and not request.META.get(
        "HTTP_X_CSRFTOKEN"
    ):
        return JsonResponse({"error": "CSRF token missing"}, status=403)

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        model = data.get("model", "models/gemini-2.0-flash-lite-preview-02-05")
    except Exception:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    user = request.user
    chat_id = request.session.get("chat_id")
    chat = (
        Chat.objects.get(id=chat_id, user=user)
        if chat_id
        else Chat.objects.create(user=user, title=f"Chat with Gemini ({model})")
    )
    request.session["chat_id"] = chat.id

    # Build raw chat history from stored messages.
    raw_chat_history = [
        {"role": msg.sender, "content": msg.content}
        for msg in Message.objects.filter(chat=chat).order_by("created_at")
    ]

    # Sanitize roles: map 'ai' to 'model' for Gemini API compatibility.
    valid_roles = {"user", "model"}
    sanitized_history = []
    for message in raw_chat_history:
        role = message.get("role")
        if role == "ai" or role == "assistant":  # Handle both 'ai' and 'assistant'
            role = "model"
        if role not in valid_roles:
            role = "user"  # Default to user if role is invalid
        sanitized_history.append({"role": role, "content": message.get("content")})

    # Append the new user prompt.
    sanitized_history.append({"role": "user", "content": prompt})

    # Create a generator for streaming tokens from Gemini.
    token_stream = stream_gemini_completion(sanitized_history, model_name=model)

    # Save the user prompt immediately.
    Message.objects.create(chat=chat, sender="user", content=prompt)

    # Helper generator to stream tokens and accumulate the full reply.
    def stream_and_save():
        full_reply = ""
        try:
            for token in token_stream:
                if "Error:" in token:  # check for error
                    full_reply += token
                    yield token
                    break  # stop streaming the rest
                full_reply += token
                yield token
        except Exception as e:
            full_reply += f"Error: {str(e)}"
            yield f"Error: {str(e)}"
        finally:
            # After streaming is complete (or an error occurs), save the assistant's full reply.
            Message.objects.create(chat=chat, sender="ai", content=full_reply)

    return StreamingHttpResponse(stream_and_save(), content_type="text/plain")
