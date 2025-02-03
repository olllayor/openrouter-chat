import json
import os
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import (
    login_required,
)  # If needed for login protection
from .models import UserProfile, Chat, Message
from django.contrib.auth.models import User
from dotenv import load_dotenv

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


@csrf_exempt
def ask_chat(request):
    # Only allow POST requests
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    # Parse the request body
    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        model = data.get("model", "")
    except Exception:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    user = request.user

    # 1. Retrieve or create Chat session
    chat_id = request.session.get("chat_id")
    if chat_id:
        try:
            chat = Chat.objects.get(id=chat_id, user=user)
        except Chat.DoesNotExist:
            # If the chat doesn't exist, create a new one
            chat = Chat.objects.create(user=user, title=f"Chat with {model}")
            request.session["chat_id"] = chat.id
    else:
        # If no chat_id in session, create a new chat
        chat = Chat.objects.create(user=user, title=f"Chat with {model}")
        request.session["chat_id"] = chat.id

    # 2. Fetch User API Token
    api_key_to_use = OPENROUTER_API_KEY
    try:
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.api_token:
            api_key_to_use = user_profile.api_token
    except UserProfile.DoesNotExist:
        pass

    # 3. Build the message history
    messages_history = []
    previous_messages = Message.objects.filter(chat=chat).order_by("created_at")
    for msg in previous_messages:
        messages_history.append({"role": msg.sender, "content": msg.content})
    messages_history.append({"role": "user", "content": prompt})

    # 4. Create the payload for the OpenRouter API
    payload = {
        "model": model,
        "messages": messages_history,
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {api_key_to_use}",
        "Content-Type": "application/json",
        "HTTP-Referer": request.META.get("HTTP_REFERER", ""),  # Add referer header
        "X-Title": "Django Chat App",  # Add a title header
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

            # Handle non-200 responses
            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                yield f"Error: {error_msg}\n"
                Message.objects.create(chat=chat, sender="user", content=prompt)
                Message.objects.create(
                    chat=chat, sender="ai", content=f"Error: {error_msg}"
                )
                return

            # Process the streaming response
            for line in response.iter_lines(decode_unicode=True):
                if not line or line.isspace():
                    continue

                if line.startswith(": "):  # Skip processing messages
                    continue

                if line.startswith("data: "):
                    line = line[6:]  # Remove "data: " prefix

                try:
                    json_data = json.loads(line)

                    # Handle error in response data
                    if "error" in json_data:
                        error_msg = json_data["error"].get("message", "Unknown error")
                        if isinstance(error_msg, dict) and "message" in error_msg:
                            error_msg = error_msg["message"]
                        yield f"Error: {error_msg}\n"
                        Message.objects.create(chat=chat, sender="user", content=prompt)
                        Message.objects.create(
                            chat=chat, sender="ai", content=f"Error: {error_msg}"
                        )
                        return

                    # Extract token from the response
                    token = (
                        json_data.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )

                    if token:
                        yield token + "\n"
                        ai_response_content += token

                except json.JSONDecodeError:
                    print(f"Failed to decode JSON: {line}")
                    continue

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            yield f"Error: {error_msg}\n"
            Message.objects.create(chat=chat, sender="user", content=prompt)
            Message.objects.create(
                chat=chat, sender="ai", content=f"Error: {error_msg}"
            )
            return

        # Save messages after successful streaming
        if ai_response_content:
            Message.objects.create(chat=chat, sender="user", content=prompt)
            Message.objects.create(chat=chat, sender="ai", content=ai_response_content)

    return StreamingHttpResponse(event_stream(), content_type="text/plain")