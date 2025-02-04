import json
import os
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import (
    login_required,
)
from .models import UserProfile, Chat, Message
from django.contrib.auth.models import User
from dotenv import load_dotenv
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.conf import settings

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

OPENROUTER_CHAT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_ENDPOINT = (
    "https://openrouter.ai/api/v1/models?supported_parameters=free"
)


def index(request):
    """
    Render the chat interface.
    """
    return render(request, "chat/index.html")


def get_models(request):
    """
    Proxy the OpenRouter API /api/v1/models endpoint.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(OPENROUTER_MODELS_ENDPOINT, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return JsonResponse({"error": "Could not fetch models."}, status=500)

    return JsonResponse(response.json(), safe=False)


def save_messages(chat, prompt, response_content, is_error=False):
    Message.objects.create(chat=chat, sender="user", content=prompt)
    Message.objects.create(
        chat=chat,
        sender="ai",
        content=f"Error: {response_content}" if is_error else response_content,
    )


@login_required
@csrf_exempt
def ask_chat(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "error": "Please login to continue",
                "login_url": reverse("admin:login"),  # Or your custom login URL
            },
            status=401,
        )

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    # Add CSRF check for AJAX
    if not request.headers.get("X-CSRFToken") and not request.META.get(
        "HTTP_X_CSRFTOKEN"
    ):
        return HttpResponseForbidden("CSRF token missing")

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        model = data.get("model", "")
    except Exception:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    user = request.user
    chat_id = request.session.get("chat_id")
    chat = (
        Chat.objects.get(id=chat_id, user=user)
        if chat_id
        else Chat.objects.create(user=user, title=f"Chat with {model}")
    )
    request.session["chat_id"] = chat.id

    api_key_to_use = OPENROUTER_API_KEY
    try:
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.api_token:
            api_key_to_use = user_profile.api_token
    except UserProfile.DoesNotExist:
        pass

    messages_history = [
        {"role": msg.sender, "content": msg.content}
        for msg in Message.objects.filter(chat=chat).order_by("created_at")
    ]
    messages_history.append({"role": "user", "content": prompt})

    payload = {"model": model, "messages": messages_history, "stream": True}
    headers = {
        "Authorization": f"Bearer {api_key_to_use}",
        "Content-Type": "application/json",
        "HTTP-Referer": request.META.get("HTTP_REFERER", ""),
        "X-Title": "Django Chat App",
    }

    def event_stream():
        ai_response_content = ""
        try:
            response = requests.post(
                OPENROUTER_CHAT_ENDPOINT,
                headers=headers,
                json=payload,
                stream=True,
                timeout=60,
            )

            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                save_messages(chat, prompt, error_msg, is_error=True)
                yield f"Error: {error_msg}\n"
                return

            for line in response.iter_lines(decode_unicode=True):
                if not line or line.isspace():
                    continue

                # Skip [DONE] messages
                if line == "data: [DONE]" or line == "[DONE]":
                    continue

                if line.startswith("data: "):
                    line = line[6:]

                try:
                    json_data = json.loads(line)
                    if "error" in json_data:
                        error_msg = json_data["error"].get("message", "Unknown error")
                        save_messages(chat, prompt, error_msg, is_error=True)
                        yield f"Error: {error_msg}\n"
                        return

                    token = (
                        json_data.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    if token:
                        ai_response_content += token
                        yield token + "\n"

                except json.JSONDecodeError:
                    # Only log if not a [DONE] message
                    if "[DONE]" not in line:
                        print(f"Failed to decode JSON: {line}")
                    continue

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            save_messages(chat, prompt, error_msg, is_error=True)
            yield f"Error: {error_msg}\n"
            return

        if ai_response_content:
            save_messages(chat, prompt, ai_response_content)

    return StreamingHttpResponse(event_stream(), content_type="text/plain")
